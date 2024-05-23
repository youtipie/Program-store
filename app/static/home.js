$(document).ready(function(){
    function get_games(data) {
        $.ajax({
            url: '/api/games',         /* Куда отправить запрос */
            method: 'get',             /* Метод запроса (post или get) */
            dataType: 'json',          /* Тип данных в ответе (xml, json, script, html). */
            data: data,     /* Данные передаваемые в массиве */
            success: function(data){   /* функция которая будет выполнена после успешного запроса.  */
                var game_list = $("ul.game-list");
                game_list.empty();
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



});

