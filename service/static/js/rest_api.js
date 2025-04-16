$(function () {

  // ****************************************
  //  U T I L I T Y   F U N C T I O N S
  // ****************************************

  // Updates the form with data from the response
  function update_form_data(res) {
      $("#wishlist_id").val(res.id);
      $("#wishlist_name").val(res.name);
      $("#wishlist_user_id").val(res.userid);
      $("#wishlist_products").val([]);
  }

  /// Clears all form fields
  function clear_form_data() {
      $("#wishlist_name").val("");
      $("#wishlist_user_id").val("");
      $("#wishlist_products").val("");
  }

  // Updates the flash message area
  function flash_message(message) {
      $("#flash_message").empty();
      $("#flash_message").append(message);
  }

  // ****************************************
  // Create a Wishlist
  // ****************************************

  $("#create-btn").click(function () {

      let name = $("#wishlist_name").val();
      let user_id = $("#wishlist_user_id").val();
      let products = [];

      let data = {
          "name": name,
          "userid": user_id,
          "products": products,
      };

      $("#flash_message").empty();
      
      let ajax = $.ajax({
          type: "POST",
          url: "/wishlists",
          contentType: "application/json",
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
    // Retrieve a Wishlist
    // ****************************************

    $("#retrieve-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json",
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
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
      $("#wishlist_id").val("");
      $("#flash_message").empty();
      clear_form_data()
  });

})


// ****************************************
// Create a Product
// ****************************************

    $("#create-btn").click(function () {

        let name = $("#product_name").val();
        let price = $("#product_price").val();
        let category = $("#product_category").val();

        let data = {
            "name": name,
            "price": price,
            "category": category
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/products",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    });
