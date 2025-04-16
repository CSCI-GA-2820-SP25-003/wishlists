$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************
  
    // Modify your flash_message function to make the message more visible
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(
        `<div class="alert alert-success">${message}</div>`
        );
        // Make sure the message stays visible long enough for tests to see it
        $("#flash_message").show();
    }
  
    function renderWishlistResults(wishlists) {
      const body = $("#wishlist-results-body");
      body.empty();
      wishlists.forEach(w => {
        body.append(`<tr><td>${w.id}</td><td>${w.name}</td><td>${w.userid}</td><td>${w.products.length}</td></tr>`);
      });
    }
  
    function renderProductResults(products) {
      const body = $("#product-results-body");
      body.empty();
      products.forEach(p => {
        body.append(`<tr><td>${p.id}</td><td>${p.wishlist_id}</td><td>${p.name}</td><td>${p.price}</td><td>${p.quantity}</td><td>${p.is_gift}</td><td>${p.purchased}</td><td>${p.description}</td><td>${p.note}</td></tr>`);
      });
    }
    function clear_wishlist_form() {
        $("#wishlist_name").val("");
        $("#wishlist_user_id").val("");
      }
  
    function clear_product_form() {
        $("#product_id").val("");
        $("#product_name").val("");
        $("#product_price").val("");
        $("#product_description").val("");
        $("#product_quantity").val("1");
        $("#product_note").val("");
        $("#product_min_price").val("");
        $("#product_max_price").val("");
        $("#product_is_gift").prop("checked", false);
        $("#product_purchased").prop("checked", false);
      }
  
    function update_wishlist_form(res) {
      $("#wishlist_id").val(res.id);
      $("#wishlist_name").val(res.name);
      $("#wishlist_userid").val(res.userid);
    }
  
    function update_product_form(res) {
      $("#product_id").val(res.id);
      $("#product_name").val(res.name);
      $("#product_price").val(res.price);
      $("#product_description").val(res.description);
      $("#product_quantity").val(res.quantity);
      $("#product_note").val(res.note);
      $("#product_is_gift").prop("checked", res.is_gift);
      $("#product_purchased").prop("checked", res.purchased);
    }
    
    // Define the missing functions
    function clear_wishlist_form() {
      clear_form("#wishlist_form");
    }
    
    function clear_product_form() {
      clear_form("#product_form");
    }

        // Function to populate the wishlist dropdown from a list of wishlists
    function populateWishlistDropdown(wishlists) {
        // Clear current options first (except the default one)
        $("#select_wishlist_dropdown option:not(:first-child)").remove();
        
        // Add each wishlist to the dropdown
        wishlists.forEach(wishlist => {
        $("#select_wishlist_dropdown").append(
            `<option value="${wishlist.id}">${wishlist.name}</option>`
        );
        });
    }
  
  
    // ****************************************
    // CRUD for Wishlist
    // ****************************************
  
    $("#create_wishlist-btn").click(function () {
      const data = {
        name: $("#wishlist_name").val(),
        userid: $("#wishlist_user_id").val()
      };
  
      // Fixed post request
      $.ajax({
        url: "/wishlists",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function(res) {
          flash_message("Wishlist Created!");
          update_wishlist_form(res);
          renderWishlistResults([res]);
          // Add this wishlist to the dropdown
          $("#select_wishlist_dropdown").append(`<option value="${res.id}">${res.name}</option>`);
        },
        error: function(res) {
          flash_message(res.responseJSON ? res.responseJSON.message : "Error creating wishlist");
        }
      });
    });
  
  
    // ****************************************
    // CRUD for Products
    // ****************************************
  
    $("#list_products-btn").click(function () {
      const wishlist_id = $("#select_wishlist_dropdown").val();
      if (!wishlist_id) return flash_message("Select a wishlist first");
  
      $.get(`/wishlists/${wishlist_id}/products`)
        .done(renderProductResults)
        .fail(res => flash_message(res.responseJSON ? res.responseJSON.message : "Error listing products"));
    });
  
    // ****************************************
    // SEARCH FEATURES
    // ****************************************
  

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear_wishlist-btn").click(function () {
        $("#wishlist_id").val("");
        clear_wishlist_form();
        $("#flash_message").empty();
    });
      
    $("#clear-product-btn").click(function () {
        clear_product_form();
        $("#flash_message").empty();
    });
});
