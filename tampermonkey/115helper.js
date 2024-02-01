// ==UserScript==
// @name         Add magnet to 115
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       Jin Liu
// @match        http*://*/*
// @grant        GM_xmlhttpRequest
// @downloadURL https://update.greasyfork.org/scripts/402283/Add%20magnet%20to%20115.user.js
// @updateURL https://update.greasyfork.org/scripts/402283/Add%20magnet%20to%20115.meta.js
// ==/UserScript==

(function() {
    'use strict';

    function createToastElement() {
        // 创建一个新的<div>元素用作toast提醒
        var toast = document.createElement('div');
        toast.id = 'toast';
        // 设置样式以使其看起来像一个toast提醒
        toast.style.cssText = `
    display: none;
    position: fixed;
    top: 20px; /* 调整top以避免靠得太近顶部 */
    left: 50%;
    transform: translateY(-100%) translateX(-50%);
    background-color: #2777F8;
    color: white;
    padding: 20px 40px; /* 增加内边距 */
    font-size: 18px; /* 增加字体大小 */
    border-radius: 10px; /* 增加边角的圆度 */
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    font-family: Arial, sans-serif;
    font-weight: bold;
    z-index: 10000;
    transition: transform 0.5s ease, opacity 0.5s ease;
`;


        // 将这个新创建的<div>元素添加到<body>的末尾
        document.body.appendChild(toast);
    }

    function showToast(message) {
        var toast = document.getElementById("toast");
        toast.textContent = message; // 设置提醒内容
        toast.style.display = "block"; // 显示提醒
        toast.style.opacity = "0";
        setTimeout(() => {
            toast.style.transform = "translateY(0) translateX(-50%)";
            toast.style.opacity = "1";
        }, 10); // 短暂延迟确保元素已显示

        // 设置定时器，在3秒后隐藏toast
        setTimeout(() => {
            toast.style.transform = "translateY(-100%) translateX(-50%)";
            toast.style.opacity = "0";
            setTimeout(() => {
                toast.style.display = "none";
            }, 500); // 等待淡出动画完成
        }, 3000);
    }

    function add_magnet_to_115(magnet) {
        GM_xmlhttpRequest({
            method: "POST",
            url: "http://localhost:3333/add-magnet-to-115",
            data: "param1=" + magnet,
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            onload: function (response) {
                if(response.status == 200) {
                    showToast("添加成功");
                } else {
                    showToast(response.responseText);
                }
            },
            onerror: function (response) {
                showToast(response.responseText);
            }
        });
    }

    // 有些链接是动态加载的，所以设定了一个延时
    setTimeout(function() {
        inject();
    }, 2000);

    function inject() {
        createToastElement();

        // 查找所有的链接和段落元素
        var elements = document.querySelectorAll('a, p');

        Array.prototype.forEach.call(elements, function(element) {
            var text, href;

            // 处理链接元素
            if (element.tagName.toLowerCase() === 'a' && element.hasAttribute('href')) {
                href = element.getAttribute('href');
                if (href.startsWith("magnet:?") || href.startsWith("thunder://") || href.startsWith("ed2k://")) {
                    insertButton(element, href);
                }
            }

            // 处理段落元素
            if (element.tagName.toLowerCase() === 'p') {
                text = element.textContent || element.innerText;
                // 假设我们要查找的文本是 "特定文本"
                if (text.includes("下载地址")) {
                    // 在这里，我们将链接假设为段落中的文本，实际情况可能需要不同的处理
                    insertButton(element, text);
                }
            }
        });
    }

    function insertButton(targetElement, link) {
        var ele = document.createElement('a');
        ele.textContent = '115'; // 设置按钮文本
        ele.style.cssText = 'padding: 2px 5px; background-color: #2777F8; color: #FFF; border-radius: 3px; text-decoration: none; margin-right: 5px; display: inline-block;';

        ele.addEventListener('click', function(e) {
            e.preventDefault(); // 阻止链接默认行为
            add_magnet_to_115(link); // 调用函数处理点击事件
        });

        // 获取父元素的第一个子元素
        var firstChild = targetElement.firstChild;

        // 将按钮插入为父元素的第一个子元素
        targetElement.insertBefore(ele, firstChild);
    }

})();

