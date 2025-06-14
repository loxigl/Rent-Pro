import BookingsClient from './BookingsClient';
import {ToastProvider} from "@/components/ui/toast";

export const dynamic = 'force-dynamic';

export default function BookingsPage() {
    return (
        <ToastProvider>
            <BookingsClient/>;
        </ToastProvider>
    )

} 