import { createBrowserClient, createServerClient, isBrowser } from '@supabase/ssr'
import type { LayoutLoad } from './$types'

const supaKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9laG55aWpiZm94YXJ2eHdwa3prIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjc1MjcyMTEsImV4cCI6MjA0MzEwMzIxMX0.4kHNRBjVr44s6eEU4gNhH6WgiVw5jTmwZGWwyV80BGw";
const supaUrl = "https://fklteshgkeffpuebfgtx.supabase.co";

export const load: LayoutLoad = async ({ data, depends, fetch }) => {
  /**
   * Declare a dependency so the layout can be invalidated, for example, on
   * session refresh.
   */
  depends('supabase:auth')

  const supabase = isBrowser()
    ? createBrowserClient(supaUrl, supaKey, {
        global: {
          fetch,
        },
      })
    : createServerClient(supaUrl, supaKey, {
        global: {
          fetch,
        },
        cookies: {
          getAll() {
            return data.cookies
          },
        },
      })

  /**
   * It's fine to use `getSession` here, because on the client, `getSession` is
   * safe, and on the server, it reads `session` from the `LayoutData`, which
   * safely checked the session using `safeGetSession`.
   */
  const {
    data: { session },
  } = await supabase.auth.getSession()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  return { session, supabase, user }
}
