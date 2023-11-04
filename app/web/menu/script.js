document.addEventListener('DOMContentLoaded', async function() {
    await updateName();
});

eel.expose
function clicked(){
    window.location.href='../play/index.html';
}

function quit_game(){
    window.location.href='../login/login.html';
}

function openPopup() {
    var popup = document.createElement('div');
    popup.classList.add('popup');

    var botDifficultyInput = document.createElement('input');
    botDifficultyInput.type = 'number';
    botDifficultyInput.min = '1';
    botDifficultyInput.max = '20';
    botDifficultyInput.placeholder = 'Bot Difficulty (1 to 20)';

    var gameImbalanceInput = document.createElement('input');
    gameImbalanceInput.type = 'number';
    gameImbalanceInput.min = '1';
    gameImbalanceInput.max = '100';
    gameImbalanceInput.placeholder = 'Game Imbalance (0 to 100)';

    var cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.addEventListener('click', function() {
        closePopup();
    });

    var startGameButton = document.createElement('button');
    startGameButton.textContent = 'Start Game';
    startGameButton.addEventListener('click', function() {
        var botDifficulty = botDifficultyInput.value;
        var gameImbalance = gameImbalanceInput.value;

        if (botDifficulty >= 1 && botDifficulty <= 20 && gameImbalance >= 1 && gameImbalance <= 100) {
            startGame(botDifficulty, gameImbalance);
            closePopup();
        } else {
            alert('Inserire valori corretti per Bot Difficulty e Game Imbalance.');
        }
    });

    popup.appendChild(botDifficultyInput);
    popup.appendChild(gameImbalanceInput);
    popup.appendChild(cancelButton);
    popup.appendChild(startGameButton);

    document.body.appendChild(popup);
}


function closePopup() {
    var popup = document.querySelector('.popup');
    if (popup) {
        popup.remove();
    }
}

function startGame(botDifficulty, gameImbalance) {
    console.log('Starting game with botDifficulty:', botDifficulty, 'and gameImbalance:', gameImbalance);
    window.location.href='../play/index.html';
}

function multiplayer(){
    alert("Sorry...We're stil working on it");
}

 async function updateName(){
    var current_usere = await eel.get_guest_name()();
    var user = document.getElementById('userName');
    user.innerHTML = `Welcome, ${current_usere}`;
}

