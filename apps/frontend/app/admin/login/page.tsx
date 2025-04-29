import { Metadata } from 'next';
import LoginPageClient from './LoginPageClient';

export const metadata: Metadata = {
    title: 'Вход в админ-панель | Kvartiry26',
    description: 'Страница входа в административную панель управления',
};

export default function LoginPage() {
    return <LoginPageClient />;
}
