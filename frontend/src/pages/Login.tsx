import React, { useState } from 'react';
import { supabase } from '../lib/supabase';
import { useSession } from '../context/SessionContext';
import type { Observer } from '../lib/identity';

const Login: React.FC = () => {
    const { login } = useSession();
    const [pin, setPin] = useState('');
    const [error, setError] = useState('');
    const [step, setStep] = useState<'pin' | 'observer'>('pin');
    const [observers, setObservers] = useState<Observer[]>([]);
    const [selectedObserver, setSelectedObserver] = useState<string>('');
    const [loading, setLoading] = useState(false);

    const handlePinSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const { data, error: rpcError } = await supabase.rpc('verify_pin', { input_pin: pin });
            if (rpcError || !data) {
                setError('Invalid PIN. Please try again.');
                setPin('');
                return;
            }

            // PIN correct — fetch observers
            const { data: obsData, error: obsError } = await supabase
                .from('observer')
                .select('observer_id, display_name')
                .eq('is_active', true)
                .order('display_name');

            if (obsError || !obsData || obsData.length === 0) {
                setError('No active observers found in the system.');
                return;
            }

            const mapped: Observer[] = obsData.map((row: any) => ({
                observer_id: String(row.observer_id),
                observer_name: row.display_name,
                session_id: 0n,
                login_timestamp: new Date().toISOString()
            }));
            setObservers(mapped);
            setStep('observer');
        } catch (err) {
            setError('Connection error. Please check your network.');
        } finally {
            setLoading(false);
        }
    };

    const handleObserverSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedObserver) return;
        setLoading(true);

        try {
            const observer = observers.find(o => o.observer_id === selectedObserver);
            if (!observer) {
                setError('Selected observer not found.');
                return;
            }

            // Sign in anonymously to get authenticated JWT (satisfies RLS v9.8.1)
            const { error: authError } = await supabase.auth.signInAnonymously();
            if (authError) {
                setError('Authentication failed. Please try again.');
                return;
            }

            // Create session_log entry
            const { data: sessionData, error: sessionError } = await supabase
                .from('session_log')
                .insert({
                    user_name: observer.observer_name,
                    user_agent: navigator.userAgent,
                    login_timestamp: new Date().toISOString()
                })
                .select('session_id')
                .single();

            if (sessionError || !sessionData) {
                setError('Failed to create session. Please try again.');
                return;
            }

            const sessionId = sessionData.session_id;
            observer.session_id = sessionId;
            observer.login_timestamp = new Date().toISOString();

            // Set authenticated context
            login(observer, sessionId);
        } catch (err) {
            setError('Connection error. Please check your network.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <h1>🐢 Turtle Incubator</h1>
                <h2>Wisconsin Turtle Conservation</h2>

                {step === 'pin' ? (
                    <form onSubmit={handlePinSubmit} className="login-form">
                        <label htmlFor="pin-input">Enter Access PIN</label>
                        <input
                            id="pin-input"
                            type="password"
                            inputMode="numeric"
                            pattern="[0-9]*"
                            maxLength={6}
                            placeholder="6-digit PIN"
                            value={pin}
                            onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 6))}
                            autoFocus
                            disabled={loading}
                        />
                        {error && <p className="login-error">{error}</p>}
                        <button type="submit" disabled={pin.length !== 6 || loading}>
                            {loading ? 'Verifying...' : 'Unlock'}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleObserverSubmit} className="login-form">
                        <label htmlFor="observer-select">Select Observer</label>
                        <select
                            id="observer-select"
                            value={selectedObserver}
                            onChange={(e) => setSelectedObserver(e.target.value)}
                            disabled={loading}
                        >
                            <option value="">-- Choose observer --</option>
                            {observers.map((obs) => (
                                <option key={obs.observer_id} value={obs.observer_id}>
                                    {obs.observer_name}
                                </option>
                            ))}
                        </select>
                        {error && <p className="login-error">{error}</p>}
                        <div className="login-buttons">
                            <button type="button" onClick={() => { setStep('pin'); setError(''); }} disabled={loading}>
                                Back
                            </button>
                            <button type="submit" disabled={!selectedObserver || loading}>
                                {loading ? 'Signing in...' : 'Enter'}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
};

export default Login;
