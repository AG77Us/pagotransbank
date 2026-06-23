const express = require('express');
const cors = require('cors');
const app = express();

// Permite recibir datos en formato JSON y aceptar conexiones desde tu HTML
app.use(cors());
app.use(express.json());

// Ruta para procesar los pagos simulados
app.post('/payments', (req, res) => {
    const { method, amount, maskedCard } = req.body;

    console.log(`\n--- NUEVO INTENTO DE PAGO ---`);
    console.log(`Monto: ${amount}`);
    console.log(`Método: ${method === 'bank' ? 'Transferencia Bancaria' : 'Tarjeta (' + maskedCard + ')'}`);

    // Simulamos que el banco tarda 1.5 segundos en aprobarlo
    setTimeout(() => {
        console.log(`Estado: ¡Aprobado! ✅`);
        res.status(200).json({ 
            success: true, 
            message: 'Pago simulado aprobado correctamente.' 
        });
    }, 1500);
});

// Puerto dinámico para Render o 8000 para tu computadora
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
    console.log(`Servidor corriendo en el puerto ${PORT}`);
});