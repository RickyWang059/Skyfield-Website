document.addEventListener('DOMContentLoaded', (event) => {
    const questionNumberElement = document.getElementById("question-number");
    const questionElement = document.getElementById("question");
    const answerButtons = document.getElementById("answer-buttons");
    const nextButton = document.getElementById("next-btn");

    let currentQuestionIndex = 0;
    let score = 0;
    let questions = [];

    function startQuiz(){
        currentQuestionIndex = 0;
        score = 0;
        nextButton.innerHTML = "Next";
        fetch('/quiz_data')
            .then(response => response.json())
            .then(data => {
                questions = data;
                showQuestion();
            });
    }

    function showQuestion(){
        resetState();
        let currentQuestion = questions[currentQuestionIndex];
        let questionNo = currentQuestionIndex + 1;
        questionNumberElement.innerHTML = "Q" + questionNo; // 顯示題號
        questionElement.innerHTML = currentQuestion[1]; // 顯示問題

        for (let i = 2; i <= 5; i++) {
            const button = document.createElement("button");
            button.innerHTML = currentQuestion[i];
            button.classList.add("btn");
            answerButtons.appendChild(button);
            if ((i - 1) == currentQuestion[6]) {
                button.dataset.correct = true;
            }
            button.addEventListener("click", selectAnswer);
        }
    }

    function resetState(){
        nextButton.style.display = "none";
        while(answerButtons.firstChild){
            answerButtons.removeChild(answerButtons.firstChild);
        }
    }

    function selectAnswer(e){
        const selectedBtn = e.target;
        const isCorrect = selectedBtn.dataset.correct === "true";
        if(isCorrect){
            selectedBtn.classList.add("correct");
            score++;
        }else{
            selectedBtn.classList.add("incorrect");
        }
        Array.from(answerButtons.children).forEach(button => {
            if(button.dataset.correct === "true"){
                button.classList.add("correct");
            }
            button.disabled = true;
        });
        nextButton.style.display = "block";
        
    }

    function showScore(){
        resetState();
        questionElement.innerHTML = `You scored ${score} out of ${questions.length}!`;
        nextButton.innerHTML = "Play Again";
        nextButton.style.display = "block";
    }

    function handleNextButton(){
        if(currentQuestionIndex < questions.length - 1){
            currentQuestionIndex++;
            showQuestion();
        }else{
            showScore();
        }
    }

    nextButton.addEventListener("click", ()=>{
        handleNextButton();
    });

    startQuiz();
});
