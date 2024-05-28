$(document).ready(function(){
    $.ajax({
        url: '/api/categories',
        method: 'get',
        dataType: 'json',
        success: function(data){
            var category_list = $(".categories-select");
            category_list.empty();

            category_list.append(`
                <option value="">Choose categories</option>
            `);

            for (let i = 0; i < data.categories.length; i++){
                category_list.append(`
                    <option value="${data.categories[i].name}">${data.categories[i].name}</option>
                `);
            }
        }
    })

    var uploadedFiles = [];
    var apkCount = 0;
    var archiveCount = 0;
    var is_newCategory = false;
    var gameId = null;
    var game = null;
    var existing_filenames = null;

    var urlPath = window.location.pathname;

    // Extract game_id using regular expression
    var match = urlPath.match(/\/edit_game\/(\d+)/);

    if (match) {
        var gameId = parseInt(match[1]); // gameId will be the extracted integer
        loadGameDetails(gameId);
    } else {
        console.error("Game ID not found in URL");
    }

    function loadGameDetails(gameId) {
        $.ajax({
            url: `/api/game?id=${gameId}`,
            method: 'get',
            dataType: 'json',
            success: function(data){
                game = data.game;
                $(".pay-for-game").prop("checked", game.is_paid);
                $(".categories-select").val(game.category_name);
                existing_filenames = game.images_names;

                for (let i = 0; i < game.images_names.length; i++){
                    addFileRow(game.images_names[i], "image", true, game.images[i], null, null);
                }

                addFileRow("poster.jpg", "poster", true, game.poster, null, null);
                existing_filenames.push("poster.jpg");

                addFileRow(game.apk_name, "apk", true, null, game.version, null);
                existing_filenames.push(game.apk_name);

                if (game.cache_name){
                    addFileRow(game.cache_name, "cache", true, null, null, null);
                    existing_filenames.push(game.cache_name);
                }

            },
            error: function(xhr, status, error) {
                console.error('Error fetching game details:', error);
            }
        });
    }


    // Handle the Add Category button click
    $('.add-categories-but').on('click', function() {
        $('.categories-select').hide();
        $('.add-categories-but').hide();
        $('[name="new_category"]').show();
        $('.return-but').show();
        is_newCategory = true;
    });

    // Handle the Return button click
    $('.return-but').on('click', function() {
        $('.categories-select').show();
        $('.add-categories-but').show();
        $('[name="new_category"]').hide().val('');
        $('.return-but').hide();
        is_newCategory = false;
    });

    var obj = $(".select-img");
    obj.on('dragenter', function (e)
    {
        e.stopPropagation();
        e.preventDefault();
        $(this).css('border', '2px solid #0B85A1');
    });
    obj.on('dragover', function (e)
    {
         e.stopPropagation();
         e.preventDefault();
    });
    obj.on('drop', function (e)
    {

         $(this).css('border', '2px dotted #0B85A1');
         e.preventDefault();
         var files = e.originalEvent.dataTransfer.files;

         //We need to send dropped files to Server
         handleFileUpload(files,obj);
    });

    $(document).on('dragenter', function (e)
    {
        e.stopPropagation();
        e.preventDefault();
    });
    $(document).on('dragover', function (e)
    {
      e.stopPropagation();
      e.preventDefault();
      obj.css('border', '2px dotted #0B85A1');
    });
    $(document).on('drop', function (e)
    {
        e.stopPropagation();
        e.preventDefault();
    });

    function addFileRow(filename, filetype, is_prepopulated, image_url, version, file){
        if (filename.endsWith('.apk')) {
            apkCount++;
            if (apkCount > 1) {
                displayErrorMessage('Only one .apk file is allowed.');
                return;
            }
        } else if (filename.endsWith('.rar') || filename.endsWith('.zip')) {
            archiveCount++;
            if (archiveCount > 1) {
                displayErrorMessage('Only one cache file is allowed.');
                return;
            }
        }

        if (is_prepopulated == false){
            uploadedFiles.push(file);
        }

        var row = $('<tr>');
        row.data('filename', filename);
        row.data('is_prepopulated', is_prepopulated);

        var iconColumn = $('<td>').addClass('table-column');
        var icon;

        if (filetype == 'image' || filetype == 'poster') {
            icon = $('<img>').attr({
                'class': 'icon-image',
                'src': image_url,
                'alt': filename,
                'width': '55',
                'height': '55'
            });
        } else if (filename.endsWith('.apk') || filename.endsWith('.rar') || filename.endsWith('.zip')) {
            icon = `<svg aria-hidden="true" width="15" height="15" id="icon-file-empty" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                            <path d="M28.681 7.159c-0.694-0.947-1.662-2.053-2.724-3.116s-2.169-2.030-3.116-2.724c-1.612-1.182-2.393-1.319-2.841-1.319h-15.5c-1.378 0-2.5 1.121-2.5 2.5v27c0 1.378 1.122 2.5 2.5 2.5h23c1.378 0 2.5-1.122 2.5-2.5v-19.5c0-0.448-0.137-1.23-1.319-2.841zM24.543 5.457c0.959 0.959 1.712 1.825 2.268 2.543h-4.811v-4.811c0.718 0.556 1.584 1.309 2.543 2.268zM28 29.5c0 0.271-0.229 0.5-0.5 0.5h-23c-0.271 0-0.5-0.229-0.5-0.5v-27c0-0.271 0.229-0.5 0.5-0.5 0 0 15.499-0 15.5 0v7c0 0.552 0.448 1 1 1h7v19.5z">
                            </path>
                            </svg>`;
        } else {
            displayErrorMessage('Unsupported file type. Only images, .rar/.zip, and .apk files are allowed.');
            return;
        }

        iconColumn.append(icon);

        iconColumn.append(" " + filename);
        row.append(iconColumn);

        if (filename.endsWith('.apk')) {
            var versionColumn = $('<td>').addClass('table-column');
            versionColumn.append(`<input class="table-input" type="text" name="version" value="${version ? version : ''}" placeholder="Enter game version">`);
            versionColumn.append(`<select hidden name="types">
                                    <option value="apk" selected>Other</option>
                               </select>`);
            row.append(versionColumn);
        } else if (filetype == 'image' || filetype == 'poster') {
            var typeColumn = $('<td>').addClass('table-column');

            var selectField = $('<select>').addClass('file-type-select');
            selectField.attr("name", "types");
            selectField.append('<option value="image" selected>Image</option>');
            selectField.append('<option value="poster">Poster</option>');

            if (is_prepopulated){
                selectField.val(filetype);
            }

            typeColumn.append(selectField);
            row.append(typeColumn);
        } else {
            var typeColumn = $('<td>').addClass('table-column');
            typeColumn.append(`<select hidden name="types">
                                    <option value="cache" selected>Other</option>
                               </select>`);
            row.append(typeColumn);
        }

        var removeColumn = $('<td>').addClass('table-column');
        var removeIcon = `<svg aria-hidden="true" width="15" height="15" id="icon-remove" viewBox="0 0 32 32" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                              <path d="M28 4H20V0h-8v4H4v4h24V4zM4 8v24c0 1.1.9 2 2 2h20c1.1 0 2-.9 2-2V8H4zm10 18h-4v-12h4v12zm8 0h-4v-12h4v12z"/>
                          </svg>`;
        removeColumn.append(removeIcon);
        row.append(removeColumn);

        $('.files-table tbody').append(row);


        $('.files-table').off('click', '#icon-remove');

        // Event delegation to handle remove file icon click
        $('.files-table').on('click', '#icon-remove', function() {
            var fileName = $(this).closest('tr').data('filename'); // Assuming you have a class 'file-name' in your table row for file names
            var is_prepopulated = $(this).closest('tr').data('is_prepopulated');

            var removedFileIndex;
            var removedFileName;

            if (is_prepopulated) {
                removedFileIndex = existing_filenames.findIndex(function(e){return e==fileName});
            } else {
                removedFileIndex = uploadedFiles.findIndex(file => file.name === fileName);
            }

            if (removedFileIndex !== -1) { // If the file was found in the array
                if (is_prepopulated){
                    var removedFileName = existing_filenames.splice(removedFileIndex, 1)[0];
                } else {
                    var removedFile = uploadedFiles.splice(removedFileIndex, 1)[0]; // Remove file from uploadedFiles array
                    removedFileName = removedFile.name;
                }
                // Decrement the appropriate count
                if (removedFileName.endsWith('.apk')) {
                    apkCount--;
                } else if (removedFileName.endsWith('.rar') || removedFileName.endsWith('.zip')) {
                    archiveCount--;
                }
                $(this).closest('tr').remove(); // Remove the row from the table
            } else {
                console.log('File not found in the array');
            }

            console.log(uploadedFiles, existing_filenames);
        });

        // Handle change in file type select
        $('.files-table').on('change', '.file-type-select', function() {
            var selectedType = $(this).val();

            if (selectedType === 'poster') {
                $('.file-type-select').not(this).val('image');
            }
        });
    }

    function handleFileUpload(files) {
        for (var i = 0; i < files.length; i++) {
            var file = files[i];

            // Check if the file name already exists in uploadedFiles or existing_filenames
            if (existing_filenames){
                var isDuplicate = uploadedFiles.some(function(existingFile) {
                    return existingFile.name === file.name;
                }) || existing_filenames.includes(file.name);
            } else {
                var isDuplicate = uploadedFiles.some(function(existingFile) {
                    return existingFile.name === file.name;
                });
            }

            if (isDuplicate) {
                displayErrorMessage('Files with the same name are not allowed.');
                continue; // Skip adding this file
            }

            // Check if a file with the same name ending in image formats already exists
            var isDuplicateImage = uploadedFiles.some(function(existingFile) {
                var existingFileName = existingFile.name.toLowerCase();
                var newFileName = file.name.toLowerCase();

                // Check for common image extensions
                var imageExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp'];

                // Check if any existing file ends with the same extension
                return imageExtensions.some(function(ext) {
                    return existingFileName === newFileName && newFileName.endsWith(ext);
                });
            });

            if (isDuplicateImage) {
                displayErrorMessage('Files with the same name ending in image formats are not allowed.');
                continue; // Skip adding this file
            }

        if (isDuplicateImage) {
            displayErrorMessage('Files with the same name ending in image formats are not allowed.');
            continue; // Skip adding this file
        }

            var filetype = file.type.startsWith('image/') ? "image" : "other";
            var image_url = URL.createObjectURL(file);
            addFileRow(file.name, filetype, false, image_url, null, file);
        }
    }

    function displayFormErrors(formId, errors) {
        $("#" + formId + " .form-error").remove();
        $("#" + formId + " .success-message").remove();

        $.each(errors, function(field, error){
            var errorHtml = '<span style="display: block;" class="form-error">' + error + '</span>';
            $("#" + formId + " [name='" + field + "']").after(errorHtml);
        });
    }

     function displaySuccessMessage(formId, message) {
        $("#" + formId + " .form-error").remove();
        $("#" + formId + " .success-message").remove();

        var successHtml = '<div class="success-message">' + message + '</div>';
        $("#" + formId + " .add-new-game-but").before(successHtml);
    }

    $('form').on('submit', function(e) {
        e.preventDefault();

        if ((is_newCategory && $("[name='new_category']").val() == "") || (!is_newCategory && $("[name='category']").val() == "")){
            displayErrorMessage('Select a valid category');
            return;

        }

        // Validate that at least one .apk, image, or poster file is uploaded
        var hasValidFiles = false;
        var apkFound = false;
        var imageFound = false;
        var posterFound = false;

        // Check each uploaded file
        $('.files-table tbody tr').each(function() {
            var fileType = $(this).find('.file-type-select').val();

            // Check if this file is an .apk, image, or poster
            if (fileType === 'poster') {
                posterFound = true;
            } else if (fileType === 'image') {
                imageFound = true;
            }
            if ($(this).find('.table-input').length > 0) {
                apkFound = true;
            }
        });

        if (apkFound && imageFound && posterFound) {
            hasValidFiles = true;
        }

        if (!hasValidFiles) {
            // Show error message if no valid files are uploaded
            displayErrorMessage('Please upload at least one .apk, image, or poster file.');
            return; // Prevent form submission
        } else {
            // Clear error message if there were previous errors
            $('.error-message').empty();
        }

        // Check if apk version is provided
        if (!$("[name='version']").val()) {
            displayErrorMessage('Please enter a version for the .apk file.');
            return;
        }

        // Prepare form data including uploaded files
        var formData = new FormData(this);
        for (var i = 0; i < uploadedFiles.length; i++) {
            formData.append('files[]', uploadedFiles[i]);
        }

        if (existing_filenames){
            formData.append('existing_filenames', JSON.stringify(existing_filenames));
        }

        // Perform AJAX submission or other form handling
        $.ajax({
            url: $(this).attr("action"),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                displaySuccessMessage("game-form", response.message);
                document.location.href="/";
            },
            error: function(xhr, status, error) {
                var errors = xhr.responseJSON.errors;
                if (errors) {
                    displayFormErrors("game-form", errors);
                }
                console.log(error);
            }
        });
    });

    // Function to display error message
    function displayErrorMessage(message) {
        $('.error-message').text(message).css('color', 'red');
    }
});