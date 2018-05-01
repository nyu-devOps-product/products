$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.id);
        $("#product_name").val(res.name);
        $("#product_price").val(res.price);
        $("#product_image").val(res.image_id);
        $("#product_description").val(res.description);
        // $("#product_review").val(res.review_list);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_id").val("");
        $("#product_name").val("");
        $("#product_price").val("");
        $("#product_image").val("");
        $("#product_description").val("");
        // $("#product_review").val("");
        $("#product_sort").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Product
    // ****************************************

    $("#create-btn").click(function () {

        var name = $("#product_name").val();
        var price = $("#product_price").val();
        var image_id = $("#product_image").val();
        var description = $("#product_description").val();
        // var review = $("#product_review").val();

        if(name == null || name == undefined || name.length <= 0) {
          flash_message("Name attribute cannot be empty")
          return
        }

        if(price == null || price == undefined || price.length <= 0) {
          flash_message("Price attribute cannot be empty")
          return
        }

        var data = {
            "name": name,
            "price": price,
            "image_id": image_id,
            "description": description
            // "review_list": review
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/products",
            contentType:"application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Product
    // ****************************************

    $("#update-btn").click(function () {

        var product_id = $("#product_id").val();

        var name = $("#product_name").val();
        var price = $("#product_price").val();
        var image_id = $("#product_image").val();
        var description = $("#product_description").val();
        // var review = $("#product_review").val();

        var data = {
            "name": name,
            "price": price,
            "image_id": image_id,
            "description": description
            // "review_list": review
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/products/" + product_id,
                contentType:"application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Product
    // ****************************************

    $("#retrieve-btn").click(function () {

        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/products/" + product_id,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Product
    // ****************************************

    $("#delete-btn").click(function () {

        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/products/" + product_id,
            contentType:"application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data();
            flash_message("Product with ID [" + product_id + "] has been Deleted!");
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        clear_form_data();
    });

    // ****************************************
    // Search for a Product
    // ****************************************

    $("#search-btn").click(function () {
        var name = $("#product_name").val().trim().toLowerCase();
        var price = $("#product_price").val().trim().toLowerCase();
        var image_id = $("#product_image").val().trim().toLowerCase();
        var description = $("#product_description").val().trim().toLowerCase();
        // var review_list = $("#product_review").val();
        var sort = $("#product_sort").val();

        var queryString = "";

        if (name) {
            queryString += 'name=' + name
        }
        if (price) {
            if (queryString.length > 0) {
                queryString += '&price=' + price
            } else {
                queryString += 'price=' + price
            }
        }
        if (image_id) {
            if (queryString.length > 0) {
                queryString += '&image_id=' + image_id
            } else {
                queryString += 'image_id=' + image_id
            }
        }
        if (description) {
            if (queryString.length > 0) {
                queryString += '&description=' + description
            } else {
                queryString += 'description=' + description
            }
        }
        // if (review_list) {
        //     if (queryString.length > 0) {
        //         queryString += '&review_list=' + review_list
        //     } else {
        //         queryString += 'review_list=' + review_list
        //     }
        // }
        if (sort) {
            if (queryString.length > 0) {
                queryString += '&sort=' + sort
            } else {
                queryString += 'sort=' + sort
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/products?" + queryString,
            contentType:"application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped">');
            var header = '<tr>'
            header += '<th style="width:10%">ID</th>'
            header += '<th style="width:10%">Name</th>'
            header += '<th style="width:10%">Price</th>'
            header += '<th style="width:10%">Image_id</th>'
            header += '<th style="width:20%">Description</th>'
            header += '<th style="width:20%">Review_list</th></tr>'
            $("#search_results").append(header);
            for(var i = 0; i < res.length; i++) {
                product = res[i];
                var row = "<tr><td>"+product.id+"</td><td>"+product.name+"</td><td>"+product.price+"</td><td>"+product.image_id+
                "</td><td>"+product.description+"</td><td>"+product.review_list+"</td></tr>";
                $("#search_results").append(row);
            }

            $("#search_results").append('</table>');

            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });

    });

})
