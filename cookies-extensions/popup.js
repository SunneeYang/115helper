document.addEventListener('DOMContentLoaded', () => {
    // 获取按钮和输入框的引用
    const sendCookiesButton = document.getElementById('sendCookies');
    const serverAddressInput = document.getElementById('serverAddress');

    // Cookies发送成功后，显示自定义通知
    const notification = document.getElementById('notification');
    const notificationText = document.getElementById('notificationText');

    const content = document.getElementById('content');
    const notLoggedInMessage = document.getElementById('notLoggedInMessage');

    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        // 首先检查当前是否在115网站
        if (!tabs[0].url.includes('115.com')) {
            console.log('Not on 115.com website');
            content.style.display = 'none';
            notLoggedInMessage.textContent = '请先访问 115.com 网站';
            notLoggedInMessage.style.display = 'block';
            return;
        }

        chrome.cookies.getAll({domain: '115.com'}, (cookies) => {
            console.log('Checking 115.com cookies...');
            const list = document.getElementById('cookiesList');

            let neededCookies = cookies.filter(cookie => ['UID', 'CID', 'SEID'].includes(cookie.name));
            console.log('Found cookies:', cookies.length);
            console.log('Required cookies found:', neededCookies.map(c => c.name));
            
            if (neededCookies.length === 3) {
                content.style.display = 'block';
                notLoggedInMessage.style.display = 'none';

                let cookiesString = neededCookies.map(cookie => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${cookie.name}: ${cookie.value}`;
                    list.appendChild(listItem);
                    return `${cookie.name}=${cookie.value}`
                }).join(';') + ';';

                console.log('Cookie string prepared successfully');
                sendCookiesButton.dataset.cookies = cookiesString;
            } else {
                console.log('Not all required cookies found');
                content.style.display = 'none';
                notLoggedInMessage.textContent = '请先登录 115 网盘';
                notLoggedInMessage.style.display = 'block';
                sendCookiesButton.dataset.cookies = '';
            }
        });
    });

    sendCookiesButton.addEventListener('click', () => {
        console.log('Send button clicked');
        const cookiesString = sendCookiesButton.dataset.cookies;
        console.log('Cookies data:', cookiesString ? 'Found' : 'Not found');
        
        if (!cookiesString) {
            console.log('No cookies available to send');
            showNotification('请先登录115网盘', 'error');
            return;
        }

        // 获取用户输入的服务器地址
        const serverAddress = serverAddressInput.value;
        console.log('Server address:', serverAddress);

        // 检查服务器地址是否合法
        if (!isValidServerAddress(serverAddress)) {
            console.log('Invalid server address');
            showNotification('请输入有效的服务器地址', 'error');
            return;
        }

        console.log('Sending request to:', `${serverAddress}/115-cookies`);
        const encodedCookies = encodeURIComponent(cookiesString);
        console.log('Encoded cookies:', encodedCookies);
        
        fetch(`${serverAddress}/115-cookies`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `cookies=${encodedCookies}`
        })
        .then(async response => {
            console.log('Response status:', response.status);
            console.log('Response headers:', Object.fromEntries([...response.headers]));
            
            const responseText = await response.text();
            console.log('Response text:', responseText);
            
            if (response.ok) {
                return responseText;
            }
            throw new Error(`Server responded with ${response.status}: ${responseText}`);
        })
        .then(data => {
            console.log('Success:', data);
            showNotification('Cookies sent successfully!', 'success');
        })
        .catch(error => {
            console.error('Error details:', error);
            showNotification(error.message, 'error');
        });
    });
});

// 编写函数来验证服务器地址的合法性
function isValidServerAddress(address) {
    // 在此处添加服务器地址的验证逻辑，确保它是有效的
    // 示例：检查地址是否以 "http://" 或 "https://" 开头
    return address.startsWith('http://') || address.startsWith('https://');
}

let notificationTimeout = null; // 用于跟踪当前消息的 setTimeout

function showNotification(message, type) {
    const notification = document.getElementById('notification');
    const notificationText = document.getElementById('notificationText');

    // 如果有消息正在显示，先关闭之前的消息
    closeNotification();

    // 设置消息和样式
    notificationText.textContent = message;
    notification.style.display = 'block';

    // 根据样式类型设置背景颜色
    if (type === 'success') {
        notification.style.backgroundColor = '#5cb85c';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#d9534f';
    }

    // 设置消息显示时间，1秒后自动关闭
    notificationTimeout = setTimeout(() => {
        closeNotification();
    }, 1000);
}

function closeNotification() {
    const notification = document.getElementById('notification');
    // 取消之前的 setTimeout
    if (notificationTimeout) {
        clearTimeout(notificationTimeout);
    }
    notification.style.display = 'none';
}
