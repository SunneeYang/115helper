document.getElementById('openLinks').addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      chrome.scripting.executeScript({
        target: {tabId: tabs[0].id},
        function: openAllLinks
      });
    });
  });
  
  function openAllLinks() {
    const links = document.querySelectorAll('.bk-table-body-wrapper a'); // 修改选择器以匹配您的链接
    links.forEach(link => {
      if (link.href.indexOf("http") !== 0) {
        return;
      }
      console.log('Opening link:', link.href); // 确认链接被找到
      window.open(link.href, '_blank'); // 使用window.open来代替chrome.tabs.create
    });
  }
  