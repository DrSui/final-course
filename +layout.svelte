<script>
    import "./styles/styles.css"
    import { onMount, afterUpdate } from "svelte";

    onMount(() => {
        const navbtns = document.querySelectorAll(".nav-btn");
        navbtns.forEach((btn) =>{
            btn.addEventListener('click', () =>{
                console.log(btn.innerHTML.toString());
                var url = btn.innerHTML.toString();
                if(btn.innerHTML === "Home" || btn.innerHTML.toString() === "Test"){
                    url = "/";
                }
                window.location.href = url;
            });
        });

    });
    afterUpdate(() => {            
        window.addEventListener("scroll", function () {
                var header = document.querySelector("header");
                if (header) {
                    header.classList.toggle("sticky", window.scrollY > 0);
                }
            });
        var vid = document.querySelector(".vid");
        if (vid){
            vid.addEventListener("click", function() {
                if (vid){
                    document.querySelector(".intro-vid")?.classList.toggle("playing");
                }
            });
        }
    });
</script>

<header>
    <div class="logoTxt nav-btn">Test</div>
    <nav>
        <ul>
            <div class="nav-btn">Documentation</div>
        </ul>
    </nav>
    <div class="nav-btn">Log In</div>
</header>
<slot />
