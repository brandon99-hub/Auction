<?php
/**
 * Plugin Name: ProBid Django Integration
 * Description: Integrates WordPress with Django backend for ProBid auction system
 * Version: 1.0.0
 * Author: Your Name
 */

defined('ABSPATH') or die('Direct access not allowed');

class ProBidIntegration {
    private $django_url;
    private $jwt_secret;
    private $api_version = 'v1';

    public function __construct() {
        $this->django_url = get_option('probid_django_url', 'http://localhost:8000');
        $this->jwt_secret = get_option('probid_jwt_secret', 'Dvn3iJjVYe8gt9KVfsyLadfVNwNRF_DZdFu1gI3fUHtQQE-Mz4VY2gHfN3VVeTlzq94U2bR06QmU241CPvQ8Eg');

        // Add REST API endpoints
        add_action('rest_api_init', array($this, 'register_routes'));
        
        // Add authentication hooks
        add_action('wp_login', array($this, 'sync_user_login'), 10, 2);
        add_action('user_register', array($this, 'sync_user_register'), 10, 1);
        add_action('profile_update', array($this, 'sync_user_update'), 10, 2);
        
        // Add 2FA hooks
        add_action('show_user_profile', array($this, 'add_2fa_fields'));
        add_action('edit_user_profile', array($this, 'add_2fa_fields'));
        add_action('personal_options_update', array($this, 'save_2fa_fields'));
        add_action('edit_user_profile_update', array($this, 'save_2fa_fields'));
        
        // Add KYC hooks
        add_action('show_user_profile', array($this, 'add_kyc_fields'));
        add_action('edit_user_profile', array($this, 'add_kyc_fields'));
        
        // Add auction hooks
        add_action('save_post_auction', array($this, 'sync_auction'), 10, 3);
        add_action('before_delete_post', array($this, 'delete_auction'), 10, 1);

        // Add admin menu
        add_action('admin_menu', array($this, 'add_admin_menu'));
        
        // Add connection test
        add_action('admin_init', array($this, 'test_connection'));

        // Add health check
        add_action('probid_health_check', array($this, 'perform_health_check'));

    }

    public function test_connection() {
        if (isset($_GET['test_connection'])) {
            $response = wp_remote_get($this->django_url . '/api/health-check/');
            
            if (is_wp_error($response)) {
                add_settings_error(
                    'probid_connection',
                    'connection_error',
                    'Failed to connect to Django backend: ' . $response->get_error_message(),
                    'error'
                );
            } else {
                $body = json_decode(wp_remote_retrieve_body($response), true);
                if ($body['status'] === 'ok') {
                    add_settings_error(
                        'probid_connection',
                        'connection_success',
                        'Successfully connected to Django backend!',
                        'success'
                );
                }
            }
        }
    }

    public function sync_user_login($user_login, $user) {
            $this->sync_user($user);
        }

        public function sync_user_register($user_id) {
            $user = get_user_by('id', $user_id);
            $this->sync_user($user);
        }

        public function sync_user_update($user_id, $old_user_data) {
            $user = get_user_by('id', $user_id);
            $this->sync_user($user);
        }

        private function validate_user_data($user_data) {
            if (empty($user_data['username']) || empty($user_data['email'])) {
                return false;
            }
            return true;
        }        

        private function sync_user($user) {
            $user_data = array(
                'username' => $user->user_login,
                'email' => $user->user_email,
                'first_name' => $user->first_name,
                'last_name' => $user->last_name,
                'is_active' => true
            );

            error_log('Sending user data to Django: ' . json_encode($user_data));


            if (!$this->validate_user_data($user_data)) {
                error_log('Invalid user data: ' . json_encode($user_data));
                return;
            }
               
            $access_token = get_user_meta($user->ID, 'django_access_token', true);
            if ($this->is_token_expired($access_token)) {
                $access_token = $this->refresh_jwt_token($user->ID);
            }
        
            $response = wp_remote_post($this->django_url . '/api/auth/sync-user/', array(
                'headers' => array(
                    'Content-Type' => 'application/json',
                    'Authorization' => 'Bearer ' . $access_token
                ),
                'body' => json_encode($user_data)
            ));
        
            if (!is_wp_error($response)) {
                $body = json_decode(wp_remote_retrieve_body($response), true);
                if (isset($body['access_token'])) {
                    update_user_meta($user->ID, 'django_access_token', $body['access_token']);
                    update_user_meta($user->ID, 'django_refresh_token', $body['refresh_token']);
                    error_log('User synced successfully: ' . $user->user_login);
                } else {
                    error_log('Failed to sync user: ' . json_encode($body));
                }
            }

        }

    private function generate_jwt_token() {
        $header = json_encode(['typ' => 'JWT', 'alg' => 'HS256']);
        $payload = json_encode([
            'iss' => get_site_url(),
            'iat' => time(),
            'exp' => time() + 3600
        ]);

        $base64UrlHeader = str_replace(['+', '/', '='], ['-', '_', ''], base64_encode($header));
        $base64UrlPayload = str_replace(['+', '/', '='], ['-', '_', ''], base64_encode($payload));

        $signature = hash_hmac('sha256', $base64UrlHeader . "." . $base64UrlPayload, $this->jwt_secret, true);
        $base64UrlSignature = str_replace(['+', '/', '='], ['-', '_', ''], base64_encode($signature));

        $jwt = $base64UrlHeader . "." . $base64UrlPayload . "." . $base64UrlSignature;

        error_log('Generated JWT: ' . $jwt); // Log the JWT token
        return $jwt;
    }

    public function add_admin_menu() {
        add_menu_page(
            'ProBid Settings',
            'ProBid',
            'manage_options',
            'probid-settings',
            array($this, 'render_settings_page'),
            'dashicons-admin-generic'
        );
    }

    public function render_settings_page() {
        if (isset($_POST['probid_settings_nonce']) && wp_verify_nonce($_POST['probid_settings_nonce'], 'probid_settings')) {
            update_option('probid_django_url', sanitize_text_field($_POST['django_url']));
            update_option('probid_jwt_secret', sanitize_text_field($_POST['jwt_secret']));
            echo '<div class="notice notice-success"><p>Settings saved.</p></div>';
        }

        $django_url = get_option('probid_django_url');
        $jwt_secret = get_option('probid_jwt_secret');
        ?>
        <div class="wrap">
            <h1>ProBid Settings</h1>
            <form method="post" action="">
                <?php wp_nonce_field('probid_settings', 'probid_settings_nonce'); ?>
                <table class="form-table">
                    <tr>
                        <th scope="row"><label for="django_url">Django Backend URL</label></th>
                        <td>
                            <input type="url" name="django_url" id="django_url" 
                                   value="<?php echo esc_attr($django_url); ?>" class="regular-text">
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="jwt_secret">JWT Secret Key</label></th>
                        <td>
                            <input type="text" name="jwt_secret" id="jwt_secret" 
                                   value="<?php echo esc_attr($jwt_secret); ?>" class="regular-text">
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="admin_username">Admin Username</label></th>
                        <td>
                            <input type="text" name="admin_username" id="admin_username" 
                                value="<?php echo esc_attr(get_option('probid_admin_username')); ?>" class="regular-text">
                        </td>
                    </tr>
                    <tr>
                        <th scope="row"><label for="admin_password">Admin Password</label></th>
                        <td>
                            <input type="password" name="admin_password" id="admin_password" 
                                value="<?php echo esc_attr(get_option('probid_admin_password')); ?>" class="regular-text">
                        </td>
                    </tr>
                </table>
                <?php submit_button(); ?>
            </form>
        </div>
        <?php
    }

    public function add_2fa_fields($user) {
        $response = wp_remote_get($this->django_url . '/api/auth/2fa/status/', array(
            'headers' => array(
                'Authorization' => 'Bearer ' . $this->generate_jwt_token()
            )
        ));

        if (!is_wp_error($response)) {
            $data = json_decode(wp_remote_retrieve_body($response), true);
            ?>
            <h3>Two-Factor Authentication</h3>
            <table class="form-table">
                <tr>
                    <th><label for="2fa_enabled">2FA Status</label></th>
                    <td>
                        <input type="checkbox" name="2fa_enabled" id="2fa_enabled" 
                               <?php checked($data['is_enabled']); ?>>
                        <span class="description">Enable two-factor authentication</span>
                    </td>
                </tr>
                <?php if ($data['is_enabled']): ?>
                <tr>
                    <th><label>Backup Codes</label></th>
                    <td>
                        <button type="button" class="button" id="show-backup-codes">
                            Show Backup Codes
                        </button>
                        <div id="backup-codes" style="display: none;">
                            <?php echo implode('<br>', $data['backup_codes']); ?>
                        </div>
                    </td>
                </tr>
                <?php endif; ?>
            </table>
            <?php
        }
    }

    public function save_2fa_fields($user_id) {
        if (!current_user_can('edit_user', $user_id)) {
            return;
        }

        $enabled = isset($_POST['2fa_enabled']);
        
        wp_remote_post($this->django_url . '/api/auth/2fa/toggle/', array(
            'headers' => array(
                'Content-Type' => 'application/json',
                'Authorization' => 'Bearer ' . $this->generate_jwt_token()
            ),
            'body' => json_encode(array('enabled' => $enabled))
        ));
    }

    public function add_kyc_fields($user) {
        $response = wp_remote_get($this->django_url . '/api/auth/kyc/status/', array(
            'headers' => array(
                'Authorization' => 'Bearer ' . $this->generate_jwt_token()
            )
        ));

        if (!is_wp_error($response)) {
            $data = json_decode(wp_remote_retrieve_body($response), true);
            ?>
            <h3>KYC Verification</h3>
            <table class="form-table">
                <tr>
                    <th><label>Verification Status</label></th>
                    <td>
                        <?php echo esc_html($data['status']); ?>
                        <?php if ($data['status'] === 'pending'): ?>
                            <button type="button" class="button" id="start-kyc">
                                Start Verification
                            </button>
                        <?php endif; ?>
                    </td>
                </tr>
            </table>
            <?php
        }
    }

    private function sync_auction($post_id) {
        $post = get_post($post_id);
        $user_id = $post->post_author;
        $access_token = get_user_meta($user_id, 'django_access_token', true);
    
        if ($this->is_token_expired($access_token)) {
            $access_token = $this->refresh_jwt_token($user_id);
        }
    
        $auction_data = array(
            'title' => $post->post_title,
            'description' => $post->post_content,
            'author' => $user_id,
        );
    
        $response = wp_remote_post($this->django_url . '/api/auctions/sync/', array(
            'headers' => array(
                'Content-Type' => 'application/json',
                'Authorization' => 'Bearer ' . $access_token
            ),
            'body' => json_encode($auction_data)
        ));
    
        if (is_wp_error($response)) {
            error_log('Failed to sync auction with Django: ' . $response->get_error_message());
        }
    }

    private function refresh_jwt_token($user_id) {
        $refresh_token = get_user_meta($user_id, 'django_refresh_token', true);
    
        $response = wp_remote_post($this->django_url . '/api/auth/token/refresh/', array(
            'headers' => array(
                'Content-Type' => 'application/json',
            ),
            'body' => json_encode(array('refresh' => $refresh_token))
        ));
    
        if (!is_wp_error($response)) {
            $body = json_decode(wp_remote_retrieve_body($response), true);
            if (isset($body['access'])) {
                update_user_meta($user_id, 'django_access_token', $body['access']);
                return $body['access'];
            } else {
                error_log('Failed to refresh token: ' . json_encode($body));
            }
        } else {
            error_log('Failed to refresh token: ' . $response->get_error_message());
        }
    
        return null;
    }

    private function is_token_expired($token) {
        $parts = explode('.', $token);
        if (count($parts) === 3) {
            $payload = json_decode(base64_decode($parts[1]), true);
            return isset($payload['exp']) && $payload['exp'] < time();
        }
        return true;
    }
    
    private function get_admin_token() {
        $admin_token = get_option('probid_admin_access_token');
        if ($this->is_token_expired($admin_token)) {
            $admin_token = $this->refresh_admin_token();
        }
        return $admin_token;
    }

    private function refresh_admin_token() {
        $response = wp_remote_post($this->django_url . '/api/auth/token/', array(
            'headers' => array(
                'Content-Type' => 'application/json',
            ),
            'body' => json_encode(array(
                'username' => 'admin_username',
                'password' => 'admin_password'
            ))
        ));

        if (!is_wp_error($response)) {
            $body = json_decode(wp_remote_retrieve_body($response), true);
            if (isset($body['access'])) {
                update_option('probid_admin_access_token', $body['access']);
                return $body['access'];
            }
        }

        error_log('Failed to refresh admin token.');
        return null;
    }

    public function schedule_health_check() {
        if (!wp_next_scheduled('probid_health_check')) {
            wp_schedule_event(time(), 'hourly', 'probid_health_check');
        }
    }
    
    public function perform_health_check() {
        $response = wp_remote_get($this->django_url . '/api/health-check/');
        if (is_wp_error($response)) {
            error_log('Health check failed: ' . $response->get_error_message());
        } else {
            error_log('Health check successful.');
        }
    }

    public function register_routes() {
        register_rest_route('probid/v1', '/sync-user', array(
            'methods' => 'POST',
            'callback' => array($this, 'handle_sync_user'),
            'permission_callback' => '__return_true',
        ));
    
        register_rest_route('probid/v1', '/sync-auction', array(
            'methods' => 'POST',
            'callback' => array($this, 'handle_sync_auction'),
            'permission_callback' => '__return_true',
        ));
    }
    
    public function handle_sync_user($request) {
        // Handle user sync logic here
        return new WP_REST_Response(array('message' => 'User synced successfully'), 200);
    }
    
    public function handle_sync_auction($request) {
        // Handle auction sync logic here
        return new WP_REST_Response(array('message' => 'Auction synced successfully'), 200);
    }
    
    // ... rest of existing code ...
}

// Initialize plugin
function probid_integration_init() {
    new ProBidIntegration();
}
add_action('plugins_loaded', 'probid_integration_init');

// Activation hook
register_activation_hook(__FILE__, 'probid_integration_activate');
function probid_integration_activate() {
    // Add default options
    add_option('probid_django_url', 'http://localhost:8000');
    add_option('probid_jwt_secret', 'your-jwt-secret-key');
    
    // Flush rewrite rules
    flush_rewrite_rules();
}

// Deactivation hook
register_deactivation_hook(__FILE__, 'probid_integration_deactivate');
function probid_integration_deactivate() {
    // Clean up if needed
    flush_rewrite_rules();
} 