/* Share the public home page without any personal photo IDs or tracking codes. */
(() => {
  const url = 'https://app.picturepurdle.com/';
  const status = document.querySelector('#friendsStatus');
  const manual = document.querySelector('#friendsManualLink');
  async function copyLink(message = status) {
    try {
      await navigator.clipboard.writeText(url);
      message.textContent = 'Link copied! Paste it into a text, email, or social post.';
      manual.hidden = true;
    } catch {
      manual.hidden = false;
      manual.focus();
      manual.select();
      message.textContent = 'Copy the selected link, then send it to a friend.';
    }
  }
  async function shareWithFriends(message = status) {
    if (typeof navigator.share !== 'function') return copyLink(message);
    try {
      await navigator.share({
        title: 'Picturepurdle',
        text: 'A window to our world. A place for everyone! Explore the changing photo mosaic—free for everyone to view.',
        url
      });
      message.textContent = 'Thanks for sharing Picturepurdle!';
    } catch (error) {
      if (error.name === 'AbortError') {
        message.textContent = 'Sharing canceled. You can still copy the link or save the QR code.';
      } else {
        await copyLink(message);
      }
    }
  }
  document.querySelector('#friendsShare').onclick = () => shareWithFriends();
  document.querySelector('#friendsCopy').onclick = () => copyLink();
  document.querySelector('#shareHome').onclick = () => shareWithFriends(document.querySelector('#homeMessage'));
})();
