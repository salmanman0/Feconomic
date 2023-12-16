var app = new Vue({
    el: "#app",
    data: {
        product: null,
        akun: null,
        produkToko: null,
        pesan: null,
        searching: "",
        placeholder: "",
    },
    mounted: function () {
        fetch('http://hplussport.com/api/products/order/price')
            .then(response => response.json())
            .then(data => {
                this.product = data;
            });
        fetch('http://127.0.0.1:5000/akun')
            .then(response => response.json())
            .then(data => {
                this.akun = data['account'];
            });
        fetch('http://127.0.0.1:5000/produk')
            .then(response => response.json())
            .then(data => {
                this.produkToko = data['produk'];
            });
        fetch('http://127.0.0.1:5000/chat')
            .then(response => response.json())
            .then(data => {
                this.pesan = data['chat'];
            });
    },
    methods: {
        reloadData() {
            setTimeout(() => {
                // Mengganti data dengan data baru
                this.produkToko = this.produkToko
            }, 1000);
        }
    }
})