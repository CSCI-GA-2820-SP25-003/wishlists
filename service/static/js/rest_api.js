$(function () {
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Modify your flash_message function to make the message more visible

    function renderWishlistResults(wishlists) {
      const body = $("#wishlist-results-body");
      body.empty();
      wishlists.forEach(w => {
        body.append(`<tr><td>${w.id}</td><td>${w.name}</td><td>${w.userid}</td><td>${w.products.length}</td></tr>`);
      });
    }

    function flash_message(message) {
      $("#flash_message").empty();
      $("#flash_message").append(
      `<div class="alert alert-success">${message}</div>`
      );
      // Make sure the message stays visible long enough for tests to see it
      $("#flash_message").show();
    }

    function renderProductResults(products) {
      const body = $("#product-results-body");
      body.empty();
      
      if (products.length === 0) {
        body.append(`<tr><td colspan="9">No products available.</td></tr>`);
        return;
      }
      
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
      $("#is_gift").prop("checked", false);        
      $("#purchased").prop("checked", false);      
    }

    function update_wishlist_form(res) {
      $("#wishlist_id").val(res.id);
      $("#wishlist_name").val(res.name);
      $("#wishlist_user_id").val(res.userid);
    }

    function update_product_form(res) {
      $("#product_id").val(res.id);
      $("#product_name").val(res.name);
      $("#product_price").val(res.price);
      $("#product_description").val(res.description);
      $("#product_quantity").val(res.quantity);
      $("#product_note").val(res.note);
      $("#is_gift").prop("checked", res.is_gift);         
      $("#purchased").prop("checked", res.purchased);    
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
        url: "/api/wishlists",
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

    $("#retrieve_wishlist-btn").click(function () {
      const id = $("#wishlist_id").val();
      $.get(`/api/wishlists/${id}`)
        .done(res => {
          flash_message("Wishlist Retrieved!");
          update_wishlist_form(res);
          renderWishlistResults([res]);
        })
        .fail(res => flash_message(res.responseJSON ? res.responseJSON.message : "Error retrieving wishlist"));
    });
      // Populate dropdown when listing all wishlists
    $("#list_wishlists-btn").click(function () {
        $.get("/api/wishlists")
        .done(wishlists => {
            renderWishlistResults(wishlists);
            populateWishlistDropdown(wishlists);  // Add this line
        })
        .fail(res => flash_message(res.responseJSON ? res.responseJSON.message : "Error listing wishlists"));
    });

    // Also populate dropdown when the page loads
    $(document).ready(function() {
        // Fetch all wishlists and populate the dropdown
        $.get("/api/wishlists")
        .done(wishlists => {
            populateWishlistDropdown(wishlists);
            
            // If we have wishlists, get products from all wishlists
            if (wishlists && wishlists.length > 0) {
                let allProducts = [];
                let fetchedCount = 0;
                
                // Select the first wishlist in the dropdown
                const firstWishlistId = wishlists[0].id;
                $("#select_wishlist_dropdown").val(firstWishlistId);
                
                // Iterate through each wishlist and get all products
                wishlists.forEach(wishlist => {
                    $.get(`/api/wishlists/${wishlist.id}/products`)
                    .done(products => {
                        // Add products to our collection
                        allProducts = allProducts.concat(products);
                        fetchedCount++;
                        
                        // When we've fetched from all wishlists, render the results
                        if (fetchedCount === wishlists.length) {
                            flash_message("All products loaded successfully");
                            renderProductResults(allProducts);
                        }
                    })
                    .fail(res => {
                        fetchedCount++;
                        console.log(`Error loading products from wishlist ${wishlist.id}`);
                        
                        // Even if some fail, render what we have when all requests complete
                        if (fetchedCount === wishlists.length) {
                            renderProductResults(allProducts);
                            flash_message("Products loaded with some errors");
                        }
                    });
                });
            } else {
                // No wishlists available
                renderProductResults([]);
            }
        })
        .fail(res => {
            console.log("Could not load wishlists for dropdown");
            renderProductResults([]);
        });
    });

    $("#update_wishlist-btn").click(function () {
      const id = $("#wishlist_id").val();
      const data = { name: $("#wishlist_name").val(), userid: $("#wishlist_userid").val() };

      $.ajax({
        url: `/api/wishlists/${id}`,
        type: "PUT",
        contentType: "application/json",
        data: JSON.stringify(data),
        success: res => {
          flash_message("Wishlist Updated!");
          update_wishlist_form(res);
            // Update the wishlist name in the dropdown
            $(`#select_wishlist_dropdown option[value="${id}"]`).text(res.name);
        },

        error: res => flash_message(res.responseJSON ? res.responseJSON.message : "Error updating wishlist")
      });
    });

    $("#delete_wishlist-btn").click(function () {
      const id = $("#wishlist_id").val();
      $.ajax({
        url: `/api/wishlists/${id}`,
        type: "DELETE",
        success: () => {
          flash_message("Wishlist Deleted!");
          clear_form("#wishlist_form");
        },
        error: res => flash_message(res.responseJSON ? res.responseJSON.message : "Error deleting wishlist")
      });
    });

    $("#delete-product-btn").click(function () {

      const id = $("#product_id").val();
      const wishlist_id = $("#select_wishlist_dropdown").val();

      $.ajax({
        url: `/api/wishlists/${wishlist_id}/products/${id}`,
        type: "DELETE",
        success: () => {
          flash_message("Product Deleted!");
          clear_form("#product_form");
        },
        error: res => flash_message(res.responseJSON ? res.responseJSON.message : "Error deleting product")
      });
    })



    $("#search_wishlist-btn").click(function () {
      const name = $("#wishlist_name").val();
      let url = "/api/wishlists";
      if (name) url += `?name=${encodeURIComponent(name)}`;

      $.get(url)
        .done(renderWishlistResults)
        .fail(res => flash_message(res.responseJSON ? res.responseJSON.message : "Error searching wishlists"));
    });


    // ****************************************
    // CRUD for Products
    // ****************************************
    
    // Adding Product to Wishlist
    $("#create_product-btn").click(function () {
      const wishlist_id = $("#select_wishlist_dropdown").val();
      if (!wishlist_id) return flash_message("Select a wishlist first");

      const data = {
        wishlist_id: parseInt(wishlist_id),  
        name: $("#product_name").val(),
        price: parseFloat($("#product_price").val()),
        quantity: parseInt($("#product_quantity").val()),
        description: $("#product_description").val(),
        note: $("#product_note").val(),
        is_gift: $("#product_is_gift").is(":checked"),
        purchased: $("#product_purchased").is(":checked")
      };
      

      $.ajax({
        url: `/api/wishlists/${wishlist_id}/products`,
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function (res) {
          flash_message("Product Added to Wishlist!");
          update_product_form(res);
          renderProductResults([res]);
        },
        error: function (res) {
          flash_message(res.responseJSON ? res.responseJSON.message : "Error adding product to wishlist");
        }
      });
    });

    $("#list_products-btn").click(function () {
      const wishlist_id = $("#select_wishlist_dropdown").val();
      if (!wishlist_id) return flash_message("Select a wishlist first");

      $.get(`/api/wishlists/${wishlist_id}/products`)
        .done(renderProductResults)
        .fail(res => flash_message(res.responseJSON ? res.responseJSON.message : "Error listing products"));
    });

    $("#retrieve_product-btn").click(function () {
      const wishlist_id = $("#select_wishlist_dropdown").val();
      const product_id = $("#product_id").val();

      if (!wishlist_id || !product_id) {
        return flash_message("Please select a wishlist and enter a product ID");
      }

      $.get(`/api/wishlists/${wishlist_id}/products/${product_id}`)
        .done(res => {
          flash_message("Product Retrieved!");
          update_product_form(res);
          renderProductResults([res]);
        })
        .fail(res => {
          flash_message(res.responseJSON ? res.responseJSON.message : "Error retrieving product");
        });
    });

    $("#filter_product-btn").click(function () {
      const wishlist_id = $("#select_wishlist_dropdown").val();
      const product_name = $("#product_filter_by_name").val().toLowerCase();
      const min_price = $("#product_min_price").val();
      const max_price = $("#product_max_price").val();


      if (!wishlist_id) {
        return flash_message("Select a wishlist first");
      }
    
      // Build query parameters
      let params = {};
      if (product_name) params.product_name = product_name;
      if (min_price) params.min_price = min_price;
      if (max_price) params.max_price = max_price;
    
      $.get(`/api/wishlists/${wishlist_id}/products`, params)
        .done(renderProductResults)
        .fail(res =>
          flash_message(res.responseJSON ? res.responseJSON.message : "Error filtering products")
        );
    });

    $("#clear-filter-btn").click(function () {
      $("#product_filter_by_name").val("");
      $("#list_products-btn").click(); // re-list all products
    });

    $("#update_product-btn").click(function () {
      let product_id = $("#product_id").val();
      let wishlist_id = $("#select_wishlist_dropdown").val();
      let name = $("#product_name").val();
      let price = parseFloat($("#product_price").val());
      let quantity = parseInt($("#product_quantity").val());      
      let description = $("#product_description").val();
      let note = $("#product_note").val();
      
      // Use the correct IDs that match your HTML
      let is_gift = $("#is_gift").is(":checked");
      let purchased = $("#purchased").is(":checked");
  
      let data = {
          "name": name,
          "wishlist_id": wishlist_id,
          "price": price,
          "quantity": quantity,
          "description": description,
          "note": note,
          "is_gift": is_gift,
          "purchased": purchased
      };
  
      $("#flash_message").empty();
  
      let path = `/api/wishlists/${wishlist_id}/products/${product_id}`;
  
      let ajax = $.ajax({
          type: "PUT",
          url: path,
          contentType: "application/json",
          data: JSON.stringify(data),
          success: res => {
            flash_message("Product Updated!");
            update_product_form(res);
          },
          error: res => flash_message(res.responseJSON ? res.responseJSON.message + " " + path : "Error updating product")
      });
    });

    // ****************************************
    // SEARCH FEATURES
    // ****************************************
    $("#search_product-btn").click(function () {
      const wishlist_id = $("#select_wishlist_dropdown").val();
      const product_name = $("#product_name").val().toLowerCase();

      if (!wishlist_id) {
        return flash_message("Select a wishlist first");
      }
      $.get(`/api/wishlists/${wishlist_id}/products`, { product_name })
        .done(res => {
          flash_message("All products loaded successfully")
          update_product_form(res[0]);
          renderProductResults(res);
        })
        .fail(res =>
          flash_message(res.responseJSON ? res.responseJSON.message : "Error searching products")
        );
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear_wishlist-btn").click(function () {
        $("#wishlist_id").val("");
        clear_wishlist_form();
        $("#flash_message").empty();
    });

    $("#clear_product-btn").click(function () {
        clear_product_form();
        $("#flash_message").empty();
    });
});
