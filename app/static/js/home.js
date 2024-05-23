$(document).ready(function(){
    let typingTimer;
    const doneTypingInterval = 500;

    function get_games(data) {
        $('div.load-page').show();
        $('div.game-div').hide();

        $.ajax({
            url: '/api/games',
            method: 'get',
            dataType: 'json',
            data: data,
            success: function(data){
                var game_list = $("ul.game-list");
                var pagination = $("ul.pagination");

                game_list.empty();
                pagination.empty();

                for (let i = 0; i < data.games.length; i++) {
                  var rating_class = ["rating-par0", "rating-par1", "rating-par2", "rating-par3", "rating-par4", "rating-par5"][data.games[i].rating];
                  game_list.append(`
                    <li class="list-li">
                        <div class="game-card">
                            <img src="${data.games[i].poster}" alt="Game Photo" width="264">
                            <div class="game-desc">
                                <h3 class="game-title">${data.games[i].title}</h3>
                                <div class="divbut">
                                    <p class="game-categ">${data.games[i].category_name}</p>
                                    <button class="but" type="button">MORE</button>
                                </div>
                                <p class="${rating_class}">${data.games[i].rating}</p>
                            </div>
                        </div>
                    </li>
                  `);
                }
                let current_page = data.current_page;
                let total_pages = data.total_pages;
                let max_visible_buttons = 5;

                function createPageButton(text, page, is_disabled = false, is_active = false) {
                    let disabled_class = is_disabled ? 'disabled' : '';
                    let active_class = is_active ? 'active' : '';
                    pagination.append(`
                        <li class="page-item">
                            <button class="page-link ${disabled_class} ${active_class}" data="${page}">${text}</button>
                        </li>
                    `);
                }

                createPageButton('Previous', data.prev_page, data.prev_page == null);

                createPageButton(1, 1, false, current_page == 1);

                if (current_page > max_visible_buttons - 1) {
                    pagination.append(`<li class="page-item disabled"><span class="page-link">...</span></li>`);
                }

                let start_page = Math.max(2, current_page - 2);
                let end_page = Math.min(total_pages - 1, current_page + 2);

                for (let i = start_page; i <= end_page; i++) {
                    createPageButton(i, i, false, current_page == i);
                }

                if (current_page < total_pages - max_visible_buttons + 2) {
                    pagination.append(`<li class="page-item disabled"><span class="page-link">...</span></li>`);
                }

                if (total_pages > 1) {
                    createPageButton(total_pages, total_pages, false, current_page == total_pages);
                }

                createPageButton('Next', data.next_page, data.next_page == null);

                $("button.page-link").click(function(){
                    data = get_data();
                    data.page = $(this).attr("data");
                    get_games(data);
                });
            },
            complete: function(){
                $('div.load-page').hide();
                $('div.game-div').show();
            }
        });
    }

    function get_data() {
        var data = {};
        var search_val = $('.search').val();
        var category_val = $("input[name='categor']:checked").val();
        if (category_val != "") {
            data.category = category_val;
        }
        if (search_val != "") {
            data.title = search_val;
        }
        return data;
    }


    get_games();
    $("input[name='categor']").on("change", function(){
        var data = get_data();
        get_games(data);
    }) ;

    $('.search').on('input', function() {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(doneTyping, doneTypingInterval);
    });

    $('.search').on('keydown', function() {
        clearTimeout(typingTimer);
    });

    function doneTyping() {
        var data = get_data();
        get_games(data);
    }

});

