// Fonction pour rafraîchir la page en fonction du nombre d'éléments par page
function refreshPageElements() {
    var urlParams = new URLSearchParams(window.location.search);
    var page = parseInt(urlParams.get("page")) || 1;
    var elementsPerPage = parseInt(document.getElementById("elementsPerPage").value) || 10;
    var searchValue = document.querySelector('input[name="searchValue"]').value.trim().toUpperCase();

    if (page <= 0) {
        page = 1;
    }

    urlParams.set("page", page.toString());
    urlParams.set("elementsPerPage", elementsPerPage.toString());
    urlParams.set("searchValue", searchValue);

    localStorage.setItem("searchValue", searchValue);
    localStorage.setItem("elementsPerPage", elementsPerPage);

    window.location.search = urlParams.toString();
}

document.addEventListener("DOMContentLoaded", function () {
    var elementsPerPageInput = document.getElementById("elementsPerPage");
    var searchInput = document.querySelector('input[name="searchValue"]');

    if (elementsPerPageInput) {
        var storedElementsPerPage = localStorage.getItem("elementsPerPage");
        if (storedElementsPerPage) {
            elementsPerPageInput.value = storedElementsPerPage;
        }
        elementsPerPageInput.addEventListener("change", refreshPageElements);
    }

    if (searchInput) {
        var storedSearchValue = localStorage.getItem("searchValue") || "";
        searchInput.value = storedSearchValue;
    }
});

// Fonction de recherche
function searchTable() {
    var searchValue = document.querySelector('input[name="searchValue"]').value.trim().toUpperCase();
    var tableName = new URLSearchParams(window.location.search).get("table");
    var tableRows = document.querySelectorAll('.' + tableName + ' tbody tr');
    var recordCount = 0;

    tableRows.forEach(row => {
        var phoneValue = row.querySelector('td:nth-child(3)')?.textContent.toUpperCase() || "";
        var addressValue = row.querySelector('td:nth-child(4)')?.textContent.toUpperCase() || "";

        if (phoneValue.includes(searchValue) || addressValue.includes(searchValue)) {
            row.style.display = 'table-row';
            recordCount++;
        } else {
            row.style.display = 'none';
        }
    });

    document.getElementById('recordCount').textContent = 'Total: ' + recordCount;
    localStorage.setItem("searchValue", searchValue);
}

document.addEventListener("DOMContentLoaded", function () {
    var searchButton = document.getElementById("searchButton");
    if (searchButton) {
        searchButton.addEventListener("click", searchTable);
    }
});

// Changer de page
function updateParams(change) {
    var urlParams = new URLSearchParams(window.location.search);
    var page = parseInt(urlParams.get("page")) || 1;
    var elementsPerPage = parseInt(document.getElementById("elementsPerPage").value) || 10;
    var totalItems = parseInt(document.querySelector('.lead')?.textContent.match(/\d+/)?.[0] || "0") - 1;

    page += change;
    if (page < 1) page = 1;
    if ((page - 1) * elementsPerPage > totalItems) page--;

    urlParams.set("page", page.toString());
    window.location.search = urlParams.toString();
}

// Aller à une page spécifique
function goToPage() {
    var pageNumber = parseInt(document.getElementById("pageNumberInput").value);
    if (!isNaN(pageNumber) && pageNumber >= 1) {
        var urlParams = new URLSearchParams(window.location.search);
        urlParams.set("page", pageNumber.toString());
        window.location.search = urlParams.toString();
    }
}

// Gestion de la sidebar
document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("sidebarToggleBtn");
    const sidebarToggleBtnInSidebar = document.getElementById("toggleSidebarBtn");

    sidebar.addEventListener("shown.bs.collapse", function () {
        toggleBtn.classList.add("d-none");
        sidebarToggleBtnInSidebar.classList.remove("d-none");
    });

    sidebar.addEventListener("hidden.bs.collapse", function () {
        toggleBtn.classList.remove("d-none");
        sidebarToggleBtnInSidebar.classList.add("d-none");
    });
});


