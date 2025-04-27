import { Metadata } from 'next';
import LoginPageClient from './LoginPageClient';

export const metadata: Metadata = {
    title: 'Вход в админ-панель | AvitoRentPro',
    description: 'Страница входа в административную панель управления',
};

export default function LoginPage() {
    return <LoginPageClient />;
}
