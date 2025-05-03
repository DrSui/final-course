import { createClient } from "@supabase/supabase-js";

const supaKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZrbHRlc2hna2VmZnB1ZWJmZ3R4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3NjY3NTEsImV4cCI6MjA1OTM0Mjc1MX0.BhSwhtkS80lyUA5tQivk6J9gwaqA8qMyOCSDAPdLzpI";
const supaUrl = "https://fklteshgkeffpuebfgtx.supabase.co";

export const supaClient = createClient(supaUrl, supaKey);
