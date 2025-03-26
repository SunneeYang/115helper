function openLinks() {
    // https://sehuatang.net/forum.php?mod=viewthread&tid=2235673&extra=page%3D5%26filter%3Dtypeid%26typeid%3D684
    // https://sehuatang.net/forum.php?mod=viewthread&tid=2235673&extra=page%3D5%26filter%3Dtypeid%26typeid%3D684
    const pattern = /^https:\/\/sehuatang\.net\/thread-(\d+)-(\d+)-(\d+)\.html/;
    // const pattern = /^https:\/\/sehuatang\.net\/forum\.php\?mod=viewthread&tid=(\d+)&extra=.*?page%3D(\d+)/;
    const links = document.querySelectorAll('.icn a'); // 修改选择器以匹配您的链接
    links.forEach(link => {
      const matches = pattern.exec(link);
      if (!matches || matches.length < 3) {
        return
      }

      const id = matches[1]
      const page = matches[2]

      if (id < 2200000) {
        return
      }
      
      console.log('Opening link:', link.href, "id:", id, "page:", page); // 确认链接被找到
      window.open(link.href, '_blank'); // 使用window.open来代替chrome.tabs.create
    });
  }
  
openLinks();
  
