// Thêm một sản phẩm vô cart
// book_detail.html
function addToCart(book_id, customer_id, quantity=1) {
    fetch("/api/carts", {
        method: "POST",
        body: JSON.stringify({
            "book_id": book_id,
            "customer_id": customer_id,
            "quantity": quantity,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => {
        if(res.status === 401) {
            window.location.href = '/login'
        } else {
            return res.json();
        }
    }).then(data => {
        let items = document.getElementsByClassName("cart-counter");
        for (let item of items)
            item.innerText = data.total_quantity;
    }).catch(err => {
        alert('Đã sảy ra lỗi không xác định!');
        console.error('error: ', err)
    });
}


//xóa một sản phẩm khỏi cart
//cart.html
function removeCart(cart_id) {
    console.log('helo')
    fetch("/api/remove_cart", {
        method: 'POST',
        body: JSON.stringify({
            "cart_id": cart_id,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => {
        if(res.status === 400) {
            alert("Không có sản phẩm nào để xóa.");
            throw new Err("Bad Request: No product to delete.");

        }else {
            return res.json();
        }
    }).then(data => {
//            alert("Sản phẩm đã được xóa khỏi giỏ hàng.");
            window.location.reload();
    }).catch(err => {
        console.error("Fetch error:", err);
        alert("Có lỗi xảy ra khi xóa sản phẩm!!!");
    });
}


// Thay đổi số lượng sản phẩm trong cart
// cart.html
function changeCart(cart_id, quantity, customer_id, stock_quantity, price) {
    if (quantity > stock_quantity) {
        alert('Số lượng tối đa còn lại là ' + stock_quantity + '\nXin lỗi vì sự bất tiện này')
        document.getElementById(cart_id).value = stock_quantity;
        quantity = stock_quantity;
    }

    if (quantity < 0) {
        alert('Số lượng tối thiểu là 1\nHãy xóa sản phẩm nếu bạn không muốn mua')
        document.getElementById(cart_id).value = 0;
        quantity = 0;
    }

    fetch("/api/change_cart", {
        method: 'POST',
        body: JSON.stringify({
            "cart_id": cart_id,
            "quantity": quantity,
            "customer_id": customer_id,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => {
        if(res.status === 400) {
            alert("Không có sản phẩm nào để xóa.");
            throw new Err("Bad Request: No product to delete.");
        }else {
            return res.json();
        }
    }).then(data => {
        let items = document.getElementsByClassName("cart-counter");

        for (let item of items)
            item.innerText = data.total_quantity;

        document.getElementById("cart-stat").innerText = data.total_quantity;
        document.getElementById("total-amount").innerText = data.total_amount.toLocaleString() + "VNĐ";
        document.getElementById("totalPrice").value = data.total_amount.toLocaleString();
        document.getElementById(`quantity_${cart_id}`).innerText = quantity;
        document.getElementById(`unit_price_${cart_id}`).innerText = (quantity*price).toLocaleString() + "VNĐ";

//        window.location.reload();
    });
}


function isAuthUser() {
    fetch("/api/carts", {
            method: "POST",
        }).then(res => {
            if(res.status === 401) {
                window.location.href = '/login'
            } else {
                return
            }
        }).catch(err => {
            alert('Đã sảy ra lỗi không xác định!');
            console.error('error: ', err)
        });
}


// Mua sản phẩm với stripe
//bood_id và quantity là mua ở trong book_detail
// customer_id là mua trong cart
function payment(book_id, quantity, customer_id) {
    fetch("/create-checkout-session", {
        method: 'POST',
        body: JSON.stringify({
            "book_id": book_id,
            "quantity": quantity,
            "customer_id": customer_id,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => {
        if(res.status === 401) {
            window.location.href = '/login'
        } else {
            return res.json(); // chuyêển res thành đối tượng js
        }
    }).then(result => {
        window.location.href = result.checkout_url
    }).catch(err => {
        alert('Đã sảy ra lỗi không xác định!');
        console.error('error: ', err)
    });
}


function checkoutOffline(book_id, quantity, customer_id) {
    fetch("/api/checkout_in_store", {
        method: 'POST',
        body: JSON.stringify({
            "book_id": book_id,
            "quantity": quantity,
            "customer_id": customer_id,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => {
        if(res.status === 401) {
            window.location.href = '/login'
            return
        }
        if(res.status === 200) {
            alert('Đơn hàng của bạn đã được lưu \nVui lòng tới cửa hàng để nhận hàng và thanh toán'); // chuyêển res thành đối tượng js
            window.location.reload();
        } else {
            alert('Đã sảy ra lỗi không xác định!');
        }
    }).catch(err => {
        alert('Đã sảy ra lỗi không xác định!');
        console.error('error: ', err)
    });
}


function demo() {
    console.log('1')
}

