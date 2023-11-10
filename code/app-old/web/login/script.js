eel.expose
function playAsGuest(){
    eel.frontend_add_guest()();
    window.location.href='../menu/menu.html';
    console.log('guest_added')
}