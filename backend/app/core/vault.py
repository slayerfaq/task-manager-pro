"""
Vault Integration Module
Управление секретами и конфигурацией через HashiCorp Vault
"""
import hvac
import os
import logging
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger(__name__)


class VaultClient:
    """Клиент для работы с HashiCorp Vault"""
    
    def __init__(self):
        self.vault_addr = os.getenv("VAULT_ADDR", "http://10.10.0.70:8200/")
        self.vault_token = os.getenv("VAULT_TOKEN")
        self.vault_role = os.getenv("VAULT_ROLE", "task-manager")
        self.namespace = os.getenv("VAULT_NAMESPACE", "")
        
        # Пути к секретам в Vault
        self.secrets_path = os.getenv("VAULT_SECRETS_PATH", "secret/data/task-manager")
        
        self.client: Optional[hvac.Client] = None
        self._connect()
    
    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _connect(self):
        """Подключение к Vault с повторными попытками"""
        try:
            logger.info("connecting_to_vault", addr=self.vault_addr)
            
            self.client = hvac.Client(
                url=self.vault_addr,
                token=self.vault_token,
                namespace=self.namespace
            )
            
            # Для Kubernetes auth
            if not self.vault_token and os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
                self._kubernetes_auth()
            
            if not self.client.is_authenticated():
                raise Exception("Vault authentication failed")
            
            logger.info("vault_connected", authenticated=True)
            
        except Exception as e:
            logger.error("vault_connection_failed", error=str(e))
            raise
    
    def _kubernetes_auth(self):
        """Аутентификация через Kubernetes Service Account"""
        try:
            with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as f:
                jwt = f.read()
            
            response = self.client.auth.kubernetes.login(
                role=self.vault_role,
                jwt=jwt,
                mount_point="kubernetes"
            )
            
            self.client.token = response["auth"]["client_token"]
            logger.info("kubernetes_auth_successful")
            
        except Exception as e:
            logger.error("kubernetes_auth_failed", error=str(e))
            raise
    
    def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """
        Получение секрета из Vault
        
        Args:
            path: путь к секрету (например, 'database/config')
            key: конкретный ключ в секрете (если нужен только один)
        
        Returns:
            Значение секрета или словарь всех секретов
        """
        try:
            full_path = f"{self.secrets_path}/{path}"
            logger.info("reading_secret", path=full_path)
            
            # Читаем секрет (KV v2 engine)
            secret = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.secrets_path.split('/')[0]
            )
            
            data = secret['data']['data']
            
            if key:
                return data.get(key)
            return data
            
        except Exception as e:
            logger.error("failed_to_read_secret", path=path, error=str(e))
            raise
    
    def get_database_config(self) -> Dict[str, str]:
        """Получение конфигурации базы данных из Vault"""
        try:
            config = self.get_secret("database/config")
            logger.info("database_config_loaded", host=config.get('host'))
            return {
                'host': config.get('host', 'postgres'),
                'port': config.get('port', '5432'),
                'database': config.get('database', 'taskdb'),
                'user': config.get('username', 'taskuser'),
                'password': config.get('password'),
            }
        except Exception as e:
            logger.warning("using_fallback_db_config", error=str(e))
            return {
                'host': os.getenv('DB_HOST', 'postgres'),
                'port': os.getenv('DB_PORT', '5432'),
                'database': os.getenv('DB_NAME', 'taskdb'),
                'user': os.getenv('DB_USER', 'taskuser'),
                'password': os.getenv('DB_PASSWORD', 'changeme'),
            }
    
    def get_redis_config(self) -> Dict[str, str]:
        """Получение конфигурации Redis из Vault"""
        try:
            config = self.get_secret("redis/config")
            return {
                'host': config.get('host', 'redis'),
                'port': config.get('port', '6379'),
                'password': config.get('password'),
                'db': config.get('db', '0'),
            }
        except Exception as e:
            logger.warning("using_fallback_redis_config", error=str(e))
            return {
                'host': os.getenv('REDIS_HOST', 'redis'),
                'port': os.getenv('REDIS_PORT', '6379'),
                'password': os.getenv('REDIS_PASSWORD'),
                'db': os.getenv('REDIS_DB', '0'),
            }
    
    def get_app_config(self) -> Dict[str, Any]:
        """Получение конфигурации приложения из Vault"""
        try:
            config = self.get_secret("app/config")
            logger.info("app_config_loaded")
            return {
                'secret_key': config.get('secret_key'),
                'algorithm': config.get('algorithm', 'HS256'),
                'access_token_expire_minutes': int(config.get('access_token_expire_minutes', 30)),
                'admin_username': config.get('admin_username', 'admin'),
                'admin_password': config.get('admin_password'),
                'api_title': config.get('api_title', 'Task Manager API'),
                'api_version': config.get('api_version', '1.0.0'),
                'cors_origins': config.get('cors_origins', '*').split(','),
                'debug': config.get('debug', 'false').lower() == 'true',
            }
        except Exception as e:
            logger.warning("using_fallback_app_config", error=str(e))
            return {
                'secret_key': os.getenv('SECRET_KEY', 'insecure-secret-key-change-me'),
                'algorithm': 'HS256',
                'access_token_expire_minutes': 30,
                'admin_username': 'admin',
                'admin_password': 'admin',
                'api_title': 'Task Manager API',
                'api_version': '1.0.0',
                'cors_origins': ['*'],
                'debug': False,
            }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Получение конфигурации мониторинга"""
        try:
            config = self.get_secret("monitoring/config")
            return {
                'enabled': config.get('enabled', 'true').lower() == 'true',
                'prometheus_port': int(config.get('prometheus_port', 9090)),
                'log_level': config.get('log_level', 'INFO'),
            }
        except Exception as e:
            logger.warning("using_fallback_monitoring_config", error=str(e))
            return {
                'enabled': True,
                'prometheus_port': 9090,
                'log_level': 'INFO',
            }
    
    def refresh_secrets(self):
        """Обновление всех секретов (можно вызывать периодически)"""
        logger.info("refreshing_secrets")
        try:
            # Переподключаемся к Vault
            self._connect()
            logger.info("secrets_refreshed")
        except Exception as e:
            logger.error("failed_to_refresh_secrets", error=str(e))
            raise


# Глобальный экземпляр Vault клиента
vault_client = VaultClient()
