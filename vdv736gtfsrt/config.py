

class Configuration:

    @classmethod
    def default_config(cls, config):
        # some of the default config keys are commented in order to force
        # the user to provide these configurations actively
        
        default_config = {
            'app': {
                #'adapter': {
                #    'type': 'nvbw.ems'
                #    'url': 'https://yourdomain.dev/[alertId]
                #},
                'endpoint': '/gtfsrt-service-alerts.pbf',
                #'participants': 'participants.yaml',
                #'subscriber': 'PY_TEST_SUBSCRIBER',
                #'publisher': 'PY_TEST_PUBLISHER',
                'pattern': 'publish/subscribe',
                'status_request_interval': 300,
                'data_update_interval': 60,
                'timezone': 'Europe/Berlin',
                'caching_enabled': False
            },
            'caching': {
                'caching_server_endpoint': '[YourCachingServerEndpoint]',
                'caching_server_ttl_seconds': 120
            }
        }

        return cls._merge_config(default_config, config)
    
    @classmethod
    def _merge_config(cls, defaults: dict, actual: dict) -> dict:
        if isinstance(defaults, dict) and isinstance(actual, dict):
            return {k: cls._merge_config(defaults.get(k, {}), actual.get(k, {})) for k in set(defaults) | set(actual)}
        
        return actual if actual else defaults