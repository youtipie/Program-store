function scroll_to_games(){
        $([document.documentElement, document.body]).animate({
            scrollTop: $(".search").offset().top
        }, 0);
    }

$(document).ready(function(){
    let typingTimer;
    const doneTypingInterval = 500;

    function getUserStatus(){
        $.ajax({
            url: `api/get_user_status`,
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    if (response.user_status == "Admin"){
                        $(".change-icon").show();
                        $(".delete-icon").show();
                        $(".change-category-icon").show();
                        $(".delete-category-icon").show();
                    }
                } else {
                    console.error('Failed to retrieve user status:', response.message);
                }
            },
            error: function(err) {
                $(".change-icon").hide();
                $(".delete-icon").hide();
                $(".change-category-icon").hide();
                $(".delete-category-icon").hide();
                console.error('Error retrieving user status:', err);
            }
        });
    }

    function updateCategoryList(){
        $.ajax({
            url: '/api/categories',
            method: 'get',
            dataType: 'json',
            success: function(data){
                var category_list = $("div.categories-div div.form");
                category_list.empty();

                category_list.append(`
                    <label class="form-label">
                        ALL GAMES
                        <input type="radio" id="all_games" name="categor" value="" checked/>
                    </label>
                `);

                for (let i = 0; i < data.categories.length; i++){
                    category_list.append(`
                        <label class="form-label">
                            <svg class="delete-category-icon" style="display: none;" data-category-name="${data.categories[i].name}" width="32" height="28" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path fill="#c31d1d" d="M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z"/></svg>
                            <svg class="change-category-icon" style="display: none;" data-category-id="${data.categories[i].id}" data-category-name="${data.categories[i].name}" width="32" height="28" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path fill="#FFD43B" d="M471.6 21.7c-21.9-21.9-57.3-21.9-79.2 0L362.3 51.7l97.9 97.9 30.1-30.1c21.9-21.9 21.9-57.3 0-79.2L471.6 21.7zm-299.2 220c-6.1 6.1-10.8 13.6-13.5 21.9l-29.6 88.8c-2.9 8.6-.6 18.1 5.8 24.6s15.9 8.7 24.6 5.8l88.8-29.6c8.2-2.7 15.7-7.4 21.9-13.5L437.7 172.3 339.7 74.3 172.4 241.7zM96 64C43 64 0 107 0 160V416c0 53 43 96 96 96H352c53 0 96-43 96-96V320c0-17.7-14.3-32-32-32s-32 14.3-32 32v96c0 17.7-14.3 32-32 32H96c-17.7 0-32-14.3-32-32V160c0-17.7 14.3-32 32-32h96c17.7 0 32-14.3 32-32s-14.3-32-32-32H96z"/></svg>
                            ${data.categories[i].name}
                            <input type="radio" name="categor" value="${data.categories[i]}"/>
                        </label>
                    `);
                }

                $("input[name='categor']").on("change", function(){
                    var data = get_data();
                    get_games(data);
                });

                category_list.append(`
                    <select class="select-sorting" name="sorting" id="sorting">
                        <option value=""></option>
                        <option value="popularity">The most popular</option>
                        <option value="rating">Rating</option>
                        <option value="title">Alphabetically</option>
                        <option value="last_changed">Last updated</option>
                        <option value="apk_size">Apk size</option>
                        <option value="cache_size">Cache size</option>
                        <option value="category_id">Category</option>
                    </select>
                `);

                getUserStatus();

                $(".select-sorting").on("change", function(){
                    var data = get_data();
                    data.page = $(".active").attr("data");
                    get_games(data);
                });

                $(".change-category-icon").click(function(event){
                    event.preventDefault();
                    event.stopPropagation();

                    category_name = $(this).data("category-name");
                    category_id = $(this).data("category-id");
                    var category_select = $(this).parent();

                    category_select.html('<input type="text" class="category-input" value="' + category_name + '">');

                    $('.category-input').focus();

                    $('.category-input').keypress(function(e) {
                        if (e.which == 13) {
                            var newCategoryName = $(this).val();

                            $.ajax({
                                url: `api/rename_category?name=${newCategoryName}&id=${category_id}`,
                                method: 'POST',
                                success: function(response) {
                                    if (response.success) {
                                        updateCategoryList();
                                        get_games();
                                    } else {
                                        console.error('Failed to delete category:', response.message);
                                    }
                                },
                                error: function(err) {
                                    alert(err.responseJSON.message);
                                    console.error('Error deleting category:', err);
                                }
                            });
                        }
                    });
                });

                $(".delete-category-icon").click(function(event){
                    event.preventDefault();
                    event.stopPropagation();

                    category_name = $(this).data("category-name");

                    $.ajax({
                        url: `api/delete_category?name=${category_name}`,
                        method: 'DELETE',
                        success: function(response) {
                            if (response.success) {
                                updateCategoryList();
                            } else {
                                console.error('Failed to delete category:', response.message);
                            }
                        },
                        error: function(err) {
                            alert(err.responseJSON.message);
                            console.error('Error deleting category:', err);
                        }
                    });
                });
            }
        })
    }

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
                                <h3 class="game-title">${data.games[i].title} <svg class="change-icon" style="display: none;" data-game-id="${data.games[i].id}" width="32" height="28" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--!Font Awesome Free 6.5.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path fill="#FFD43B" d="M471.6 21.7c-21.9-21.9-57.3-21.9-79.2 0L362.3 51.7l97.9 97.9 30.1-30.1c21.9-21.9 21.9-57.3 0-79.2L471.6 21.7zm-299.2 220c-6.1 6.1-10.8 13.6-13.5 21.9l-29.6 88.8c-2.9 8.6-.6 18.1 5.8 24.6s15.9 8.7 24.6 5.8l88.8-29.6c8.2-2.7 15.7-7.4 21.9-13.5L437.7 172.3 339.7 74.3 172.4 241.7zM96 64C43 64 0 107 0 160V416c0 53 43 96 96 96H352c53 0 96-43 96-96V320c0-17.7-14.3-32-32-32s-32 14.3-32 32v96c0 17.7-14.3 32-32 32H96c-17.7 0-32-14.3-32-32V160c0-17.7 14.3-32 32-32h96c17.7 0 32-14.3 32-32s-14.3-32-32-32H96z"/></svg>
                                <svg class="delete-icon" style="display: none;" data-game-id="${data.games[i].id}" width="32" height="28" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path fill="#c31d1d" d="M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z"/></svg></h3>
                                <div class="divbut">
                                    <p class="game-categ">${data.games[i].category_name}</p>
                                    <button class="but" data-game-url="${data.games[i].game_url}" data-game-id="${data.games[i].id}">MORE</button>
                                </div>
                                <p class="${rating_class}">${data.games[i].rating}</p>
                            </div>
                        </div>
                    </li>
                  `);
                }

                getUserStatus();

                $(".change-icon").click(function(){
                    game_id = $(this).data("game-id");
                    window.location.href = `/edit_game/${game_id}`
                });

                $(".delete-icon").click(function(){
                    game_id = $(this).data("game-id");

                    $.ajax({
                        url: `api/delete_game?game_id=${game_id}`,
                        method: 'DELETE',
                        success: function(response) {
                            if (response.success) {
                                var data = get_data();
                                data.page = $(".active").attr("data");
                                get_games(data);
                            } else {
                                console.error('Failed to delete game:', response.message);
                            }
                            },
                        error: function(err) {
                            $(".game-desc svg").hide();
                            console.error('Error deleting game:', err);
                        }
                    });
                });

                $(".game-desc .divbut button.but").click(function(){
                   game_id = $(this).data("game-id");
                   gameUrl = $(this).data("game-url");

                   window.location = gameUrl;
                   $.ajax({
                       url: `api/add_popularity?game_id=${game_id}`,
                       method: 'POST',
                       success: function(response) {
                               console.log("Added popularity!");
                        },
                        error: function(err) {
                           console.error('Error getting token:', err);
                        }
                   });
                });

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
                    pagination.append(`<li class="page-item"><span class="page-link disabled">...</span></li>`);
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
        scroll_to_games();
        var data = {};
        var search_val = $('.search').val();
        var category_val = $("input[name='categor']:checked").val();
        if (category_val != "") {
            data.category = category_val;
        }
        if (search_val != "") {
            data.title = search_val;
        }
        order_value = $(".select-sorting").val();
        if (order_value){
            data.order = order_value;
        }
        return data;
    }

    updateCategoryList();
    get_games();

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

