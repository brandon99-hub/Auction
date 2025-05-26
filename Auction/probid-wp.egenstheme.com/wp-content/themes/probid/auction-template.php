<?php
/**
 * Template Name: Auction Display
 */

get_header();

// Get auction data from Django
$auction_id = get_the_ID();
$django_url = 'https://your-django-backend.com';
$response = wp_remote_get($django_url . '/api/auctions/' . $auction_id . '/');

if (!is_wp_error($response)) {
    $auction = json_decode(wp_remote_retrieve_body($response), true);
?>

<div class="auction-container">
    <div class="auction-header">
        <h1><?php echo esc_html($auction['title']); ?></h1>
        <div class="auction-meta">
            <span class="status"><?php echo esc_html($auction['status']); ?></span>
            <span class="time-remaining" data-end="<?php echo esc_attr($auction['end_time']); ?>"></span>
        </div>
    </div>

    <div class="auction-content">
        <div class="auction-images">
            <?php
            foreach ($auction['item']['images'] as $image) {
                echo '<img src="' . esc_url($image['url']) . '" alt="' . esc_attr($auction['title']) . '">';
            }
            ?>
        </div>

        <div class="auction-details">
            <div class="current-bid">
                <h3>Current Bid</h3>
                <p class="amount"><?php echo esc_html($auction['current_price']); ?></p>
            </div>

            <div class="bid-form">
                <?php if (is_user_logged_in() && $auction['status'] === 'active'): ?>
                    <form id="place-bid-form" data-auction-id="<?php echo esc_attr($auction_id); ?>">
                        <input type="number" name="amount" min="<?php echo esc_attr($auction['current_price'] + $auction['minimum_increment']); ?>" step="0.01" required>
                        <button type="submit">Place Bid</button>
                    </form>
                <?php elseif (!is_user_logged_in()): ?>
                    <p>Please <a href="<?php echo wp_login_url(get_permalink()); ?>">login</a> to place a bid.</p>
                <?php endif; ?>
            </div>

            <div class="auction-description">
                <h3>Description</h3>
                <?php echo wp_kses_post($auction['description']); ?>
            </div>

            <div class="item-details">
                <h3>Item Details</h3>
                <ul>
                    <li>Category: <?php echo esc_html($auction['item']['category']); ?></li>
                    <li>Condition: <?php echo esc_html($auction['item']['condition']); ?></li>
                    <?php if ($auction['item']['dimensions']): ?>
                        <li>Dimensions: <?php echo esc_html($auction['item']['dimensions']); ?></li>
                    <?php endif; ?>
                    <?php if ($auction['item']['weight']): ?>
                        <li>Weight: <?php echo esc_html($auction['item']['weight']); ?></li>
                    <?php endif; ?>
                </ul>
            </div>
        </div>
    </div>

    <div class="bid-history">
        <h3>Bid History</h3>
        <div id="bid-history-list">
            <!-- Bid history will be loaded dynamically -->
        </div>
    </div>
</div>

<script>
jQuery(document).ready(function($) {
    // Handle bid placement
    $('#place-bid-form').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const auctionId = form.data('auction-id');
        const amount = form.find('input[name="amount"]').val();

        $.ajax({
            url: '<?php echo esc_js($django_url); ?>/api/auctions/' + auctionId + '/place_bid/',
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
            },
            data: {
                amount: amount
            },
            success: function(response) {
                // Update UI with new bid
                updateAuctionDisplay(response);
            },
            error: function(xhr) {
                alert('Error placing bid: ' + xhr.responseJSON.error);
            }
        });
    });

    // Update time remaining
    function updateTimeRemaining() {
        const endTime = new Date($('.time-remaining').data('end'));
        const now = new Date();
        const diff = endTime - now;

        if (diff <= 0) {
            $('.time-remaining').text('Auction ended');
            return;
        }

        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        $('.time-remaining').text(hours + 'h ' + minutes + 'm remaining');
    }

    setInterval(updateTimeRemaining, 60000);
    updateTimeRemaining();

    // Load bid history
    function loadBidHistory() {
        $.ajax({
            url: '<?php echo esc_js($django_url); ?>/api/auctions/' + <?php echo $auction_id; ?> + '/bids/',
            method: 'GET',
            success: function(response) {
                const historyList = $('#bid-history-list');
                historyList.empty();

                response.forEach(function(bid) {
                    historyList.append(`
                        <div class="bid-item">
                            <span class="bidder">${bid.user.username}</span>
                            <span class="amount">${bid.amount}</span>
                            <span class="time">${new Date(bid.created_at).toLocaleString()}</span>
                        </div>
                    `);
                });
            }
        });
    }

    loadBidHistory();
    setInterval(loadBidHistory, 30000);
});
</script>

<?php
} else {
    echo '<p>Error loading auction data.</p>';
}

get_footer(); 