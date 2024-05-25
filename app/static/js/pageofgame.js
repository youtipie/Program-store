function scroll_to_comments(){
    $([document.documentElement, document.body]).animate({
        scrollTop: $("#comment").offset().top
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
                            $.ajax({
                                url: `api/add_download_count`,
                                method: 'POST',
                                success: function(response) {
                                    if (response.success) {
                                        console.log(response.message);
                                    } else {
                                        console.error('Failed to add download_count:', response.message);
                                    }
                                    },
                                error: function(err) {
                                    console.error('Error adding download_count:', err);
                                }
                            });
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
                                        <p class="user-nickname">${comment.username} <svg data-comment-id="${comment.id}" data-game-id="${data.game_id}" width="28" height="20" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path fill="#c31d1d" d="M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z"/></svg></p>
                                    </div>
                                    <p class="comment-time">${comment.date}</p>
                                    <p class="comment">${comment.content}
                                    </p>
                                </div>
                            `);
                        });

                        $.ajax({
                            url: `api/get_user_status`,
                            method: 'GET',
                            success: function(response) {
                                if (response.success) {
                                    if (response.user_status == "Admin"){
                                        $(".user-nickname svg").show();
                                    }
                                } else {
                                    console.error('Failed to retrieve user status:', response.message);
                                }
                                },
                            error: function(err) {
                                $(".user-nickname svg").hide();
                                console.error('Error retrieving user status:', err);
                            }
                        });

                        $(".user-nickname svg").click(function(){
                            game_id = $(this).data("game-id");
                            comment_id = $(this).data("comment-id");

                            $.ajax({
                                url: `api/delete_comment?game_id=${game_id}&comment_id=${comment_id}`,
                                method: 'DELETE',
                                success: function(response) {
                                    if (response.success) {
                                        var data = {"game_id": gameId};
                                        data.page = $(".active").attr("data");
                                        fetchGameComments(data);
                                    } else {
                                        console.error('Failed to delete comment:', response.message);
                                    }
                                    },
                                error: function(err) {
                                    $(".game-desc svg").hide();
                                    console.error('Error deleting comment:', err);
                                }
                            });
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

    function getQueryParam(param) {
        const urlParams = (new URL(location.href)).searchParams;
        return urlParams.get(param);
    }

    let gameId = getQueryParam('id');
    if (gameId) {
        fetchGameData(gameId);
        fetchGameComments({"game_id": gameId});
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

    $(".rating-but").click(function(){
        rating = parseInt($(this).text());

        $.ajax({
            url: `api/rate_game?game_id=${gameId}&rating=${rating}`,
            method: 'POST',
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
});