import * as baileys from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import qrcode from 'qrcode';
import fs from 'fs';
import path from 'path';
import axios from 'axios';
import config from './config.js';
import logger from './logger.js';
import { randomDelay, formatPhoneNumber, isValidPhoneNumber } from './utils.js';

const makeWASocket = baileys.default?.default || baileys.default || baileys.makeWASocket || baileys;
const useMultiFileAuthState = baileys.useMultiFileAuthState || baileys.default?.useMultiFileAuthState;
const DisconnectReason = baileys.DisconnectReason || baileys.default?.DisconnectReason;

class WhatsAppHandler {
    constructor(sessionId = 'default') {
        this.sessionId = sessionId;
        this.sessionDir = path.join(config.sessionsDir, sessionId);
        this.socket = null;
        this.qrCode = null;
        this.isConnected = false;
        this.connectionStatus = 'disconnected';

        if (!fs.existsSync(this.sessionDir)) {
            fs.mkdirSync(this.sessionDir, { recursive: true });
        }
    }

    async connect() {
        try {
            logger.info('Initializing WhatsApp connection');
            const { state, saveCreds } = await useMultiFileAuthState(this.sessionDir);
            this.socket = makeWASocket({
                auth: state,
                printQRInTerminal: false,
                browser: ['WhatsApp Agent', 'Chrome', '1.0.0'],
                logger,
            });

            this.socket.ev.on('connection.update', async (update) => {
                const { connection, lastDisconnect, qr } = update;
                if (qr) {
                    this.qrCode = await qrcode.toDataURL(qr);
                    this.connectionStatus = 'qr_ready';
                }
                if (connection === 'open') {
                    this.isConnected = true;
                    this.connectionStatus = 'connected';
                    this.qrCode = null;
                } else if (connection === 'close') {
                    this.isConnected = false;
                    this.connectionStatus = 'disconnected';
                    setTimeout(() => this.connect(), 5000);
                }
            });
            this.socket.ev.on('creds.update', saveCreds);
        } catch (error) {
            logger.error('Failed to connect:', error);
        }
    }

    getQRCode() { return this.qrCode; }
    isWhatsAppConnected() { return this.isConnected; }
    getConnectionStatus() { return { status: this.connectionStatus, isConnected: this.isConnected }; }
}
export default WhatsAppHandler;
