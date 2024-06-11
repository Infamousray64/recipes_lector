window.onload = function() {
    var statusFilter = document.getElementById("status-filter");
    var urlParams = new URLSearchParams(window.location.search);
    var status = urlParams.get('status');
    if (status) {
        statusFilter.value = status;
    }

    statusFilter.onchange = function() {
        var status = this.value;
        switch (status) {
            case "todos":
                window.location.href = "/filter?status=todos";
                break;
            case "procesado":
            case "no procesado":
            case "en proceso":
            case "cotizado parcial":
            case "cotizado total":
            case "facturado parcial":
            case "facturado total":
                window.location.href = "/filter?status=" + encodeURIComponent(status);
                break;
            default:
                window.location.href = "/filter";
                break;
        }
    }
}