import {redirect} from "@sveltejs/kit";
import { supaClient } from "$lib/supabase";

export const GET = async (event) => {
    const{
        url,
    } = event;
    const code = url.searchParams.get("code") as string;
    const next = url.searchParams.get("next") ?? "/";
    
    if (code) {
        const {error} = await supaClient.auth.exchangeCodeForSession(code)
        if (!error){
            throw redirect(303,"");
        }
    }

    throw redirect(303,"")
};
