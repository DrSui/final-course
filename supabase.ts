import { createClient } from "@supabase/supabase-js";

const supaKey = "PRIVATE KEY";
const supaUrl = "PRIVATE URL";

export const supaClient = createClient(supaUrl, supaKey);
