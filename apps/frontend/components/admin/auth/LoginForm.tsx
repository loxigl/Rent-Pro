"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface LoginFormProps {
    onSuccess?: () => void;
}

const LoginForm = ({ onSuccess }: LoginFormProps) => {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            // Выполняем запрос на аутентификацию
            const response = await fetch(`${API_URL}/admin/api/v1/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Не удалось выполнить вход');
            }

            // Сохраняем токены в localStorage
            localStorage.setItem('accessToken', data.access_token);
            localStorage.setItem('refreshToken', data.refresh_token);
            localStorage.setItem('tokenTimestamp', Date.now().toString());

            // Вызываем колбэк успешного входа
            if (onSuccess) {
                onSuccess();
            } else {
                // По умолчанию перенаправляем на dashboard
                router.push('/admin');
            }
        } catch (err: any) {
            setError(err.message || 'Произошла ошибка при входе');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
            <h1 className="text-2xl font-bold mb-6 text-center">Вход в админ-панель</h1>

            {error && (
                <div className="bg-red-50 text-red-700 p-3 rounded-md mb-4">
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                        Email
                    </label>
                    <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                        required
                    />
                </div>

                <div className="mb-6">
                    <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                        Пароль
                    </label>
                    <input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                        required
                    />
                </div>

                <Button
                    type="submit"
                    className="w-full"
                    disabled={isLoading}
                >
                    {isLoading ? 'Вход...' : 'Войти'}
                </Button>
            </form>
        </div>
    );
};

export default LoginForm;