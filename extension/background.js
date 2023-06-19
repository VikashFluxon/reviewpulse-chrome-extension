let url;

// init = (tab) => {
//     const { id, url } = tab;
//     chrome.scripting.executeScript({
//         target: { tabId: id, allFrames: true },
//         files: ["./foreground.js"]
//     })
//         .then(() => {
//             console.log("INJECTED THE FOREGROUND SCRIPT.");
//         });
//     console.log("Loading information about the product")
// }

// chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
//     console.log(tab.url)
//     if (changeInfo.status === 'complete' && /^http/.test(tab.url)) {




//         chrome.scripting.insertCSS({
//             target: { tabId: tabId },
//             files: ["./foreground_styles.css"]
//         })
//             .then(() => {
//                 console.log("INJECTED THE FOREGROUND STYLES.");

//                 chrome.scripting.executeScript({
//                     target: { tabId: tabId },
//                     files: ["./foreground.js"]
//                 })
//                     .then(() => {
//                         console.log("INJECTED THE FOREGROUND SCRIPT.");
//                     });
//             })
//             .catch(err => console.log(err));
//     }
// });

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.message === 'get_product_and_rating') {

        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            console.log("tabs", tabs)
            console.log("tabId", tabs[0].id)
            chrome.scripting.executeScript(
                {
                    target: { tabId: tabs[0].id },
                    func: () => {
                        let rating=0;
                        const productTitleElement = document.getElementById("productTitle");
                        const ratingElement = document.getElementById("acrPopover");
                        if(ratingElement){
                            rating = ratingElement.title.split(" ")[0];
                        }
                        let productTitle = productTitleElement ? productTitleElement.innerText : null;
                        return { productTitle: productTitle, rating: rating };
                    }
                },
                function (result) {
                    const productTitle = result[0].result.productTitle;
                    const rating = result[0].result.rating;
                    if (productTitle) {
                        // Make the API call using the productTitle or perform any other logic you need
                        // For demonstration, we'll send the product title back to the popup
                        sendResponse({ message: 'success', payload: { name: productTitle, rating: rating } });
                    }
                }
            );
        });
        // sendResponse({ message: 'success', payload: { name: 'Nokia 2660 Flip 4G Volte keypad Phone with Dual SIM, Dual Screen, inbuilt MP3 Player & Wireless FM Radio | Red', rating: '4.5' } });
        // chrome.storage.local.get('product_name', data => {
        //     if (chrome.runtime.lastError) {
        //         sendResponse({
        //             message: 'fail'
        //         });
        //         return;
        //     }

        //     sendResponse({
        //         message: 'success',
        //         payload: data.name
        //     });
        // });

        return true;
    } else if (request.message === 'change_name') {
        chrome.storage.local.set({
            name: request.payload
        }, () => {
            if (chrome.runtime.lastError) {
                sendResponse({ message: 'fail' });
                return;
            }

            sendResponse({ message: 'success' });
        })

        return true;
    } else if (request.message === 'calculate_true_rating') {

        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            console.log("tabs", tabs)
            console.log("tabId", tabs[0].id)

            // chrome.cookies.getAllCookieStores(function (data) {
            //     console.log("data", data)
            // })
            chrome.cookies.getAll({}, function (cookie) {
                console.log(url)
                console.log(cookie);
                allCookieInfo = "";
                sessionToken = ""

                for (i = 0; i < cookie.length; i++) {
                    temp = cookie[i];
                    console.log(temp.name)
                    console.log(temp.value)
                    if (temp.name == 'session-token') {
                        sessionToken = temp.value;
                        break;
                    }
                    // console.log(JSON.stringify(cookie[i]));

                    // allCookieInfo = allCookieInfo + JSON.stringify(cookie[i]);
                    // console.log(allCookieInfo)
                }
                let encodedUrl = tabs[0].url
                const options = {
                    method: 'POST',
                    url: 'https://8918-2401-4900-1f3e-2bc9-4a9-68dc-8c88-853d.ngrok-free.app/v1/analyze',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ "url": encodedUrl, "token": sessionToken }),
                };

                //Testing apis
                fetch("https://8918-2401-4900-1f3e-2bc9-4a9-68dc-8c88-853d.ngrok-free.app/v1/analyze", options)
                    .then(response => response.json())
                    .then(data => {
                        console.log(data)
                        console.log(data.data.summary)
                        sendResponse({ message: 'success', rating: data.data.average_real_rating, summary: data.data.summary });
                        //great way to communicate between background and popup.js
                        // chrome.runtime.sendMessage({ action: "dataFetched", data });
                    })
                    .catch(error => {
                        console.error("Error fetching data:", error);
                        sendResponse({ message: 'failed' })
                    });

                // localStorage.setItem("currentCookieInfo", allCookieInfo);
            });
        });
        // sendResponse({ message: 'success', payload: '4' });
        return true;
    }
});