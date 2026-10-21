<?php
if (PHP_SAPI !== 'cli') exit(1);
$_SERVER['HTTP_HOST'] = '127.0.0.1:8136';
$_SERVER['REQUEST_URI'] = '/';
require dirname(__DIR__) . '/runtime/wordpress/wp-load.php';
if (($argv[1] ?? '') === 'cleanup') {
    $items = get_posts(['post_type' => 'cerlab_lead', 'post_status' => 'private', 'numberposts' => -1, 'title' => 'QA local demo']);
    foreach ($items as $item) wp_delete_post($item->ID, true);
}
$leads = get_posts(['post_type' => 'cerlab_lead', 'post_status' => 'private', 'numberposts' => -1, 'title' => 'QA local demo']);
echo json_encode(['version' => get_bloginfo('version'), 'block_theme' => wp_is_block_theme(), 'parent' => get_template(),
    'products' => wp_count_posts('cerlab_product')->publish, 'categories' => wp_count_terms(['taxonomy' => 'cerlab_category', 'hide_empty' => false]),
    'home_id' => get_option('page_on_front'), 'test_leads' => count($leads),
    'greenshift' => is_plugin_active('greenshift-animation-and-page-builder-blocks/plugin.php'), 'roles' => get_user_by('login', 'yuri')->roles,
    'can_read' => user_can(get_user_by('login','yuri'), 'read'), 'can_edit' => user_can(get_user_by('login','yuri'), 'edit_posts')], JSON_UNESCAPED_UNICODE);
