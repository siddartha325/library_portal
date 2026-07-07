document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // BOOK SEARCH & GENRE FILTER
    // ==========================================

    const search = document.getElementById("searchInput");
    const genre = document.getElementById("genreFilter");
    const cards = document.querySelectorAll(".book-card");

    function filterBooks() {

        const text = search.value.toLowerCase();
        const selectedGenre = genre.value;

        cards.forEach(function (card) {

            const title = card.dataset.title || "";
            const author = card.dataset.author || "";
            const bookGenre = card.dataset.genre || "";

            const matchSearch =
                title.includes(text) ||
                author.includes(text);

            const matchGenre =
                selectedGenre === "" ||
                selectedGenre === bookGenre;

            card.style.display =
                (matchSearch && matchGenre) ? "" : "none";

        });

    }

    if (search) {
        search.addEventListener("keyup", filterBooks);
    }

    if (genre) {
        genre.addEventListener("change", filterBooks);
    }


    // ==========================================
    // ISSUE DATE & DUE DATE
    // ==========================================

    const issueDate = document.getElementById("issueDate");
    const dueDate = document.getElementById("dueDate");

    if (issueDate && dueDate) {

        const today = new Date();

        issueDate.value = today.toISOString().split("T")[0];

        let due = new Date(today);

        due.setDate(due.getDate() + 14);

        dueDate.value = due.toISOString().split("T")[0];

    }


    // ==========================================
    // RETURN BOOK - LIVE FINE CALCULATOR
    // ==========================================

    const bookSelect = document.getElementById("id_book");
    const memberSelect = document.getElementById("id_member");

    const fineBox = document.getElementById("fineAmount");
    const dueDateBox = document.getElementById("dueDateDisplay");
    const lateDaysBox = document.getElementById("lateDays");

    function calculateFine() {

        if (!bookSelect || !memberSelect) return;

        if (!bookSelect.value || !memberSelect.value) {

            if (fineBox)
                fineBox.value = "₹0.00";

            if (dueDateBox)
                dueDateBox.value = "";

            if (lateDaysBox)
                lateDaysBox.value = "0";

            return;
        }

        fetch(`/calculate-fine/?book=${bookSelect.value}&member=${memberSelect.value}`)

            .then(response => response.json())

            .then(data => {

                if (fineBox)
                    fineBox.value = "₹" + data.fine;

                if (dueDateBox)
                    dueDateBox.value = data.due_date;

                if (lateDaysBox)
                    lateDaysBox.value = data.late_days;

            })

            .catch(error => {

                console.log("Fine Calculation Error:", error);

            });

    }

    if (bookSelect && memberSelect) {

        bookSelect.addEventListener("change", calculateFine);

        memberSelect.addEventListener("change", calculateFine);

    }

});