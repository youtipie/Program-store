function scroll_to_comments(){
    $([document.documentElement, document.body]).animate({
        scrollTop: $("#comments").offset().top
    }, 0);
}

$(document).ready(function() {
    $("button[data='toggle-modal']").click(function(){
        $("div.backdrop").addClass("is-open");
    });

    $(document).keydown(function(event) {
        if (event.key === "Escape") {
            $("div.backdrop").removeClass("is-open");
        }
    });

    $("div.backdrop").click(function(event) {
        if ($(event.target).hasClass("backdrop")) {
            $("div.backdrop").removeClass("is-open");
        }
    });

    function fetchGameData(gameId) {
        $.ajax({
            url: `api/game?id=${gameId}`,
            method: 'GET',
            success: function(response) {
                    if (response.success) {
                        const gameData = response.game;
                        var images_carousel = $(".carousel-inner");
                        images_carousel.empty();
                        $.each(gameData.images, function(i, image){
                            images_carousel.append(`
                               <div class="carousel-item  ${i == 0 ? 'active' : ''}">
                                    <img src="${image}" class="d-block w-100" alt="image of game">
                                </div>
                            `);
                        });

                        $(".logo-image").attr("src", gameData.poster);
                        $(".game-version").text("Version: " + gameData.version);
                        $(".subscribe").text(gameData.is_paid == true ? "PAID" : "FREE");
                        $(".game-header").text(gameData.title);
                        $(".game-version").text("Version: " + gameData.version);
                        $(".info-par").text("Category: " + gameData.category_name);
                        $(".desc").text(gameData.description);

                        $(".change-par").text("change: " + gameData.last_changed);
                        $(".version").text("v." + gameData.version);
                        $("#apk-size").text(Math.round(gameData.apk_size) + " Mb");
                        $("#apk-download").click(function(){
                            window.location = gameData.apk_url;
                        });

                        if (gameData.cache_name){
                            $(".button-div").append(`
                                <button type="button" class="down-button" id="cache-download"><svg class="icon icon-down-svg" id="icon-down-svg" viewBox="0 0 32 32">
                                    <path d="M23 14l-8 8-8-8h5v-12h6v12zM15 22h-15v8h30v-8h-15zM28 26h-4v-2h4v2z"></path>
                                </svg>
                                Download CACHE
                                <span class="but-span">${Math.round(gameData.cache_size)} Mb</span>
                                </button>
                            `);

                            $("#cache-download").click(function(){
                                window.location = gameData.cache_url;
                            });
                        }
                    } else {
                        console.error('Failed to fetch game data:', response.message);
                    }
                },
            error: function(err) {
                console.error('Error fetching game data:', err);
            }
        });
    }

    function fetchGameComments(data) {
        scroll_to_comments();
        $.ajax({
            url: `api/comments`,
            method: 'GET',
            dataType: 'json',
            data: data,
            success: function(response) {
                    if (response.success) {
                        comments_section = $("#comments");
                        comments_section.empty();

                        $(".numberofcomments").text(response.total_comments + " Comments");
                        $.each(response.comments, function(i, comment){
                            comments_section.append(`
                                <div class="comment-div">
                                    <div class="user">
                                        <img src="${comment.user_pfp}" class="comment-avatar" alt="user-avatar" width="25" height="25">
                                        <p class="user-nickname">${comment.username}</p>
                                    </div>
                                    <p class="comment-time">${comment.date}</p>
                                    <p class="comment">${comment.content}
                                    </p>
                                </div>
                            `);
                        });

                        var pagination = $("ul.pagination");
                        pagination.empty();

                        let current_page = response.current_page;
                        let total_pages = response.total_pages;
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

                        createPageButton('Previous', response.prev_page, response.prev_page == null);

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

                        createPageButton('Next', response.next_page, response.next_page == null);

                        $("button.page-link").click(function(){
                            data = {"game_id": gameId};
                            data.page = $(this).attr("data");
                            fetchGameComments(data);
                        });
                    } else {
                        console.error('Failed to fetch game comments:', response.message);
                    }
                },
            error: function(err) {
                console.error('Error fetching game comments:', err);
            }
        });
    }

    function fetchGameRatingTokens(gameId) {
        $.ajax({
            url: `api/get_rate_game_tokens?game_id=${gameId}`,
            method: 'GET',
            success: function(data) {
                if (data.success) {
                    $(".rating-but").click(function(){
                        token = data.tokens[parseInt($(this).text()) - 1];

                        $.ajax({
                            url: `api/rate_game?token=${token}`,
                            method: 'GET',
                            success: function(data) {
                                if (data.success) {
                                    alert("You successfully rated the game!")
                                } else {
                                    console.error('Failed to rate:', response.message);
                                }
                                },
                            error: function(err) {
                                alert("You have already voted!")
                                console.error('Error rating game:', err);
                            }
                        });
                    });
                } else {
                    console.error('Failed to fetch tokens:', response.message);
                }
                },
            error: function(err) {
                console.error('Error fetching tokens:', err);
            }
        });
    }

    function getQueryParam(param) {
        const urlParams = (new URL(location.href)).searchParams;
        return urlParams.get(param);
    }

    let gameId = getQueryParam('id');
    if (gameId) {
        fetchGameData(gameId);
        fetchGameComments({"game_id": gameId});
        fetchGameRatingTokens(gameId);
    } else {
        console.error('No game ID found in URL.');
    }

    function displayFormErrors(formId, errors) {
        $("#" + formId + " .form-error").remove();
        $("#" + formId + " .success-message").remove();

        $.each(errors, function(field, error){
            var errorHtml = '<span class="form-error">' + error + '</span>';
            $("#" + formId + " input[name='" + field + "']").after(errorHtml);
        });
    }

     function displaySuccessMessage(formId, message) {
        $("#" + formId + " .form-error").remove();
        $("#" + formId + " .success-message").remove();

        var successHtml = '<div class="success-message">' + message + '</div>';
        $("#" + formId + " .send-but").before(successHtml);
    }

    $("#comment-form").submit(function(event){
        event.preventDefault();
        var formData = $(this).serialize();
        $.ajax({
            type: "POST",
            url: $(this).attr("action"),
            data: formData,
            success: function(response){
                displaySuccessMessage("comment-form", response.message);
                $("#comment-form")[0].reset();
                data = {"game_id": gameId};
                fetchGameComments(data);
            },
            error: function(xhr, status, error){
                var errors = xhr.responseJSON.errors;
                if (errors) {
                    displayFormErrors("comment-form", errors);
                }
                console.log(error);
            }
        });
    });
});