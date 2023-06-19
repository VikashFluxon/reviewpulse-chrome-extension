summary = []

chrome.runtime.sendMessage({
    message: "get_product_and_rating"
}, response => {
    if (response.message === 'success') {

        document.getElementById('current-rating-text').innerHTML = `<div>Current Rating: ${response.payload.rating}<div>`;
        document.getElementById('product-name').innerText = `${response.payload.name}`;
        document.getElementById('current-rating').innerHTML = `<i data-star="${response.payload.rating}"></i>`;
        chrome.runtime.sendMessage({
            message: "calculate_true_rating"
        }, response => {
            if (response.message === 'success') {
                document.getElementById('true-rating-text').innerHTML = `<div>True Rating: ${response.rating}<div>`;
                document.getElementById('true-rating').innerHTML = `<i data-star="${response.rating}"></i>`;
                console.log(response.summary)
                summary = response.summary;
                let summaryElement = document.getElementById('summary');
                for (let i = 0; i < summary.length; i++) {
                    const elem = document.createElement("li");
                    elem.innerHTML = response.summary[i]
                    summaryElement.appendChild(elem);
                }
            } else {
                document.getElementById('summary').innerHTML = `<p>Error in processing request.<br> Please try again<p>`;
            }
        });
    } else {
        document.getElementById('product-name').innerText = `No Product found`;
    }
});

function findOut() {
    console.log("Find out")
    chrome.runtime.sendMessage({
        message: "calculate_true_rating"
    }, response => {
        if (response.message === 'success') {
            document.getElementById('true-rating-text').innerHTML = `<div>True Rating: ${response.rating}<div>`;
            document.getElementById('true-rating').innerHTML = `<i data-star="${response.rating}"></i>`;
            document.getElementById('summary').innerHTML = `<p>${response.summary}<p>`;
        } else {
            document.getElementById('summary').innerHTML = `<p>Error in processing request.<br> Please try again<p>`;
        }
    });
}

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    if (message.action === "dataFetched") {
        const data = message.data;
        const popupElement = document.getElementById("popup");
        if (popupElement && data) {
            // Customize this part to display the data as desired in the popup
            popupElement.textContent = JSON.stringify(data);
        }
    }
});