window.onload = function() {
    var statusFilter = document.getElementById("status-filter");
    var urlParams = new URLSearchParams(window.location.search);
    var status = urlParams.get('status');
    if (status) {
        statusFilter.value = status;
    }

    statusFilter.onchange = function() {
        var status = this.value;
        if (status === "todos") {
            window.location.href = "/filter?status=todos";
        } else if (status === "procesado" || status === "no procesado") {
            window.location.href = "/filter?status=" + status;
        } else {
            window.location.href = "/filter";
        }
    }
}