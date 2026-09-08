import { redirect } from "next/navigation";

interface PageProps {
  params: Promise<{
    patient_id: string;
  }>;
}

export default async function DynamicConsultationPage({ params }: PageProps) {
  const resolvedParams = await params;
  const patientId = resolvedParams.patient_id;
  redirect(`/?patient_id=${encodeURIComponent(patientId)}`);
}
