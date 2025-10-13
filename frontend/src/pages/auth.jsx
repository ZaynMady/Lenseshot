import {createClient} from '@supabase/supabase-js'
import { Auth } from '@supabase/auth-ui-react'
import { ThemeSupa } from '@supabase/auth-ui-shared'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'


export default function AuthPage(){
    const navigate = useNavigate();
    const supabaseUrl = import.meta.env.VITE_SUPABASE_PROJECT_URL;
    const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;
    const supabase = createClient(supabaseUrl, supabaseKey);
    

  useEffect(() => {
    // ✅ Check if already logged in
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) navigate('/homepage')
    })

    // ✅ Listen for login events
    const { data: listener } = supabase.auth.onAuthStateChange((event, session) => {
      if (session && event === 'SIGNED_IN') {
        navigate('/homepage')
      }
    })

    // Cleanup listener when component unmounts
    return () => {
      listener.subscription.unsubscribe()
    }
  }, [navigate])

    return (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm">
        <Auth
            supabaseClient={supabase}
            appearance={{ theme: ThemeSupa }}
            theme="dark"
            providers={['google', 'facebook', 'apple']}
        />
        </div>
    );
}