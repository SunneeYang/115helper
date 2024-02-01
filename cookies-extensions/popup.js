document.addEventListener('DOMContentLoaded', () => {
    const sendButton = document.getElementById('sendCookies');

    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        chrome.cookies.getAll({url: tabs[0].url}, (cookies) => {
            const list = document.getElementById('cookiesList');

            if (cookies.length) {
                cookies.forEach((cookie) => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${cookie.name}: ${cookie.value}`;
                    list.appendChild(listItem);
                });
            } else {
                list.textContent = 'No cookies found.';
            }
            // 过滤出 UID, CID, SEID 并转换为表单编码的字符串
            let cookiesString = cookies
                .filter(cookie => ['UID', 'CID', 'SEID'].includes(cookie.name))
                .map(cookie => `${encodeURIComponent(cookie.name)}=${encodeURIComponent(cookie.value)}`)
                .join(';') + ';';
            // 现在 cookiesString 包含了所有键值对，用分号和一个空格分隔
            console.log(cookiesString); // 或者您可以在这里做其他事情，比如显示到页面上
            // 将 cookiesString 保存起来以便稍后发送
            sendButton.dataset.cookies = cookiesString;
        });
    });

    sendButton.addEventListener('click', () => {
        const cookiesString = sendButton.dataset.cookies;
        if (cookiesString) {
            // 这里替换为你的服务器地址
            const serverUrl = 'http://localhost:3333/115-cookies';
            
            fetch(serverUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `cookies=${encodeURIComponent(cookiesString)}`
            })
            .then(response => {
                if (response.ok) {
                    return response;
                }
                throw new Error('Network response was not ok.');
            })
            .then(data => {
                console.log('Cookies sent successfully:', data);
            })
            .catch(error => {
                console.error('Error sending cookies:', error);
            });
        } else {
            console.log('No cookies to send.');
        }
    });
});
