function submitQuestion() {
    const question = document.getElementById('questionTextarea').value.trim();
    if (!question) {
        alert('Please enter a question.');
        return;
    }
    fetch('/tutor', {
        method: 'POST',
        body: JSON.stringify({ question: question }),
        headers: { 'Content-Type': 'application/json' },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok.');
        }
        return response.json();
    })
    .then(data => {
        updateUIWithAnswer(question, data.answer);
    })
    .catch(error => {
        console.error('Error:', error);
        displayError('Failed to fetch the answer. Please try again.');
    });
}

function updateUIWithAnswer(question, answer) {
    const answersDiv = document.getElementById('answers');
    const converter = new showdown.Converter();
    const answerHtml = converter.makeHtml(answer);
    
    const answerDiv = document.createElement('div');
    answerDiv.classList.add('answer');
    answerDiv.innerHTML = `<strong class="highlight">User:</strong> ${question}<br><strong class="highlight">Tutor:</strong> ${answerHtml}`;
    answersDiv.appendChild(answerDiv);

    document.getElementById('questionTextarea').value = '';
    autoResizeTextarea(); 
    hljs.highlightAll();
}

function autoResizeTextarea() {
    const textarea = document.getElementById('questionTextarea');
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

function displayError(message) {
    alert(message);
}
