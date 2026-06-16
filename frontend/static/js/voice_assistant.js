// Voice Assistant - LabGas Manager
// Versão 2.0: Cilindro, Pressão, Elemento, Amostra

(function() {
    'use strict';

    // ==================== ESTADO DO ASSISTENTE ====================
    const voiceState = {
        state: 'IDLE',           // IDLE, INTENT, COLLECTING, CONFIRMING, EXECUTE, FEEDBACK
        intent: null,           // 'cilindro', 'pressao', 'elemento', 'leitura'
        data: {},              // Dados temporários
        currentStep: 0,        // Passo atual
        confirmed: false,     // Flag de confirmação
        speaking: false,       // Flag para evitar sobreposição
        recognizing: false,   // Flag de reconhecimento
        retries: 0,          // Contador de tentativas
        maxRetries: 3          // Máximo de tentativas
    };

    // ==================== PERGUNTAS DO FORMULÁRIO ====================
    const cilindroSteps = [
        { field: 'codigo', prompt: 'Diga o código. Exemplo: zero zero um.', verify: 'código' },
        { field: 'data_compra', prompt: 'Diga a data de compra. Exemplo: quinze de janeiro.', verify: 'data' },
        { field: 'gas_kg', prompt: 'Quantos quilos de gás?', verify: 'quilos' },
        { field: 'custo', prompt: 'Qual o valor em reais?', verify: 'custo' },
        { field: 'status', prompt: 'Diga ativo ou esgotado.', verify: 'status' }
    ];

    const pressaoSteps = [
        { field: 'cilindro_id', prompt: 'Qual o código do cilindro?', verify: 'código' },
        { field: 'pressao', prompt: 'Qual a pressão em bar?', verify: 'número' },
        { field: 'temperatura', prompt: 'Qual a temperatura em graus Celsius?', verify: 'número' },
        { field: 'data', prompt: 'Qual a data?', verify: 'data' },
        { field: 'hora', prompt: 'Qual a hora?', verify: 'hora' }
    ];

    const elementoSteps = [
        { field: 'nome', prompt: 'Qual o nome do elemento?', verify: 'texto' },
        { field: 'consumo_lpm', prompt: 'Qual o consumo em litros por minuto?', verify: 'número' }
    ];

    const leituraSteps = [
        { field: 'data', prompt: 'Qual a data da leitura?', verify: 'data' },
        { field: 'tempo_chama', prompt: 'Qual o tempo de chama?', verify: 'tempo' },
        { field: 'cilindro_id', prompt: 'Qual o cilindro?', verify: 'text' },
        { field: 'elemento_id', prompt: 'Qual o elemento?', verify: 'text' },
        { field: 'quantidade', prompt: 'Qual a quantidade?', verify: 'número' }
    ];

    // Mapeamento de intents para steps
    const intentSteps = {
        'cilindro': cilindroSteps,
        'pressao': pressaoSteps,
        'elemento': elementoSteps,
        'leitura': leituraSteps
    };

    // Valores padrão por intent
    const defaultValues = {
        'cilindro': { gas_kg: '1.0', custo: '290.00', status: 'ativo' },
        'pressao': { temperatura: '25' },
        'elemento': {},
        'leitura': { quantidade: '1', hora: '00', minuto: '00', segundo: '00' }
    };

    // ==================== RECONHECIMENTO DE VOZ ====================
    let recognition = null;
    let synthesis = window.speechSynthesis;

    // Verifica suporte
    function isSpeechSupported() {
        return 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
    }

    // Inicializa reconhecimento
    function initRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return null;

        recognition = new SpeechRecognition();
        recognition.lang = 'pt-BR';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        recognition.continuous = false;

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            const confidence = event.results[0][0].confidence;
            console.log('[VOICE] Reconhecido:', transcript, '(confiança:', confidence + ')');
            processInput(transcript.toLowerCase().trim(), confidence);
        };

        recognition.onerror = function(event) {
            console.error('[VOICE] Erro no reconhecimento:', event.error);
            voiceState.recognizing = false;
            updateUI();

            if (event.error === 'not-allowed') {
                speak('Microfone não permitido. Clique no ícone de microfone do navegador para permitir.', false);
            } else if (event.error === 'no-speech') {
                speak('Não ouvi nada. Tente novamente.', false);
            } else if (event.error === 'aborted') {
                console.log('[VOICE] Reconhecimento aborted (cancelado pelo usuário)');
            } else if (event.error === 'network') {
                speak('Erro de rede. Verifique sua conexão.', false);
            } else {
                speak('Erro no reconhecimento. Tente novamente.', false);
            }
        };

        recognition.onend = function() {
            console.log('[VOICE] Reconhecimento finalizado');
            voiceState.recognizing = false;
            updateUI();
        };

        return recognition;
    }

    // ==================== SÍNTESE DE VOZ ====================
    let preventAutoRecognition = false;

    function speak(text, autoListen = true) {
        if (!synthesis || voiceState.speaking) {
            console.log('[VOICE] speak ignorado (synthesis:', !!synthesis, ', speaking:', voiceState.speaking + ')');
            return;
        }

        // Controlar se deve iniciar reconhecimento automaticamente
        preventAutoRecognition = !autoListen;

        // Para qualquer fala anterior
        synthesis.cancel();

        // Atualizar histórico visual
        addToHistory('Sistema', text);

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'pt-BR';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        utterance.onstart = function() {
            voiceState.speaking = true;
            console.log('[VOICE] Falando:', text);
        };

        utterance.onend = function() {
            voiceState.speaking = false;
            console.log('[VOICE] Fala finalizada');
            updateUI();

            // Após falar, iniciar reconhecimento APENAS se não foi usado quick-select
            // Adicionar delay para evitar erro de rede (Chrome precisa de tempo entre fala e reconhecimento)
            if (!preventAutoRecognition && (voiceState.state === 'IDLE' || voiceState.state === 'COLLECTING')) {
                setTimeout(() => {
                    if (!voiceState.speaking) {
                        startRecognition();
                    }
                }, 1500);
            }
            preventAutoRecognition = false;
        };

        utterance.onerror = function(e) {
            voiceState.speaking = false;
            console.error('[VOICE] Erro na fala:', e);
            preventAutoRecognition = false;
        };

        synthesis.speak(utterance);
        updateUI();
    }

    // ==================== HISTÓRICO VISUAL ====================
    function addToHistory(who, text) {
        const container = document.getElementById('voice-history-content');
        const wrapper = document.getElementById('voice-history');
        if (!container) return;

        const entry = document.createElement('div');
        entry.className = 'mb-1';

        const colorClass = who === 'Sistema' ? 'text-primary' : 'text-success';
        entry.innerHTML = '<span class="' + colorClass + '"><strong>' + who + ':</strong></span> ' + text;

        container.appendChild(entry);

        // Scroll após renderização para acompanhar últimas mensagens
        requestAnimationFrame(() => {
            if (wrapper) {
                wrapper.scrollTop = wrapper.scrollHeight;
            }
        });

        console.log('[VOICE] ' + who + ':', text);
    }

    // ==================== RECONHECIMENTO ====================
    function startRecognition() {
        console.log('[VOICE] startRecognition called - recognition:', !!recognition, ', recognizing:', voiceState.recognizing, ', speaking:', voiceState.speaking);

        if (!recognition) {
            console.warn('[VOICE] Recognition não inicializado');
            speak('Reconhecimento de voz não está disponível. Use Chrome ou Edge.', false);
            return;
        }

        if (voiceState.recognizing || voiceState.speaking) {
            console.log('[VOICE] startRecognition ignorado - já ativo');
            return;
        }

        // Resetar estado antes de tentar
        voiceState.recognizing = true;
        updateUI();

        try {
            recognition.start();
            console.log('[VOICE] Reconhecimento iniciado com sucesso');
        } catch (e) {
            console.error('[VOICE] Erro ao iniciar reconhecimento:', e);
            voiceState.recognizing = false;
            updateUI();

            // Mensagem de erro mais clara
            if (e.message && e.message.includes('already started')) {
                console.log('[VOICE] Reconhecimento já estava ativo, resetando...');
                try { recognition.stop(); } catch(e2) {}
            } else {
                speak('Não foi possível activar o microfone. Verifique as permissões do navegador.', false);
            }
        }
    }

    function stopRecognition() {
        if (recognition) {
            try {
                if (voiceState.recognizing) {
                    recognition.stop();
                }
            } catch(e) {
                console.log('[VOICE] Erro ao parar reconhecimento:', e);
            }
        }
        voiceState.recognizing = false;
        updateUI();
    }

    // ==================== PROCESSAMENTO DE ENTRADA ====================
    function processInput(text, confidence, fromQuickSelect = false) {
        console.log('[VOICE] processInput:', text, '| state:', voiceState.state, '| intent:', voiceState.intent, '| quickSelect:', fromQuickSelect);

        // Adicionar ao histórico
        addToHistory('Você', text);

        // Ignora confiança muito baixa (exceto quick-select que tem confidence 1.0)
        if (confidence < 0.5 && !fromQuickSelect) {
            speak('Não entendi bem. Pode repetir?', false);
            return;
        }

        // Normalizar texto
        text = text.toLowerCase().trim();

        // Estado IDLE: identificar intenção
        if (voiceState.state === 'IDLE') {
            // Verificar intents com flexibilidade
            if (text.includes('cilindro') || text === 'um' || text === '1') {
                startIntent('cilindro');
            } else if (text.includes('pressão') || text.includes('pressao') || text.includes('pressao') || text === '2') {
                startIntent('pressao');
            } else if (text.includes('elemento') || text === '3') {
                startIntent('elemento');
            } else if (text.includes('leitura') || text === '4') {
                startIntent('leitura');
            } else if (text.includes('cancelar') || text.includes('sair') || text.includes('fechar')) {
                speak('Ok. Até logo!');
                resetState();
            } else {
                speak('Desculpe, não entendi. Diga "cilindro", "pressão", "elemento" ou "leitura" para registrar.');
            }
            return;
        }

        // Estado INTENT: já temos a intenção, ir para COLLECTING
        if (voiceState.state === 'INTENT') {
            transitionTo('COLLECTING');
            const steps = intentSteps[voiceState.intent] || cilindroSteps;
            speak('Ok. ' + steps[0].prompt);
            return;
        }

        // Estado COLLECTING: coletar dados
        if (voiceState.state === 'COLLECTING') {
            processCollecting(text);
            return;
        }

        // Estado CONFIRMING: confirmação
        if (voiceState.state === 'CONFIRMING') {
            if (text.includes('sim') || text.includes('confirma') || text.includes('correto') || text === 'ok' || text === 'y' || text.includes('confirmar')) {
                transitionTo('EXECUTE');
            } else if (text.includes('não') || text.includes('nao') || text.includes('cancelar') || text.includes('errado') || text === 'n') {
                const steps = intentSteps[voiceState.intent] || cilindroSteps;
                speak('Ok. Vamos novamente. ' + steps[0].prompt);
                voiceState.currentStep = 0;
                voiceState.data = { ...defaultValues[voiceState.intent] };
                transitionTo('COLLECTING');
            } else {
                speak('Diga sim para confirmar ou não para repetir.');
            }
            return;
        }

        // Estado EXECUTE/FEEDBACK: ignorar
        if (voiceState.state === 'EXECUTE' || voiceState.state === 'FEEDBACK') {
            return;
        }
    }

    function startIntent(intentName) {
        const steps = intentSteps[intentName] || cilindroSteps;
        const defaults = defaultValues[intentName] || {};

        transitionTo('INTENT', { intent: intentName });
        speak('Certo! Vou registrar um novo ' + intentName + '. ' + steps[0].prompt);
        voiceState.currentStep = 0;
        voiceState.data = { ...defaults };
    }

    function processCollecting(text) {
        const currentSteps = intentSteps[voiceState.intent] || cilindroSteps;
        const step = currentSteps[voiceState.currentStep];
        if (!step) return;

        let value = text;
        let isValid = true;

        // Processar conforme campo
        switch (step.field) {
            case 'codigo':
                value = parseCodigo(text);
                if (!value || !value.match(/^CIL-\d{3}$/)) {
                    speak('Código inválido. Diga apenas os números, como zero zero um.');
                    isValid = false;
                }
                break;

            case 'data_compra':
            case 'data':
                value = parseData(text);
                if (!value) {
                    speak('Data não reconhecida. Diga no formato dia mês ano.');
                    isValid = false;
                }
                break;

            case 'gas_kg':
                value = parseNumero(text);
                if (!value || value <= 0 || value > 100) {
                    speak('Quantidade inválida. Diga um número de 1 a 100.');
                    isValid = false;
                } else {
                    value = String(value);
                }
                break;

            case 'custo':
                value = parseNumero(text);
                if (!value || value <= 0) {
                    speak('Custo inválido. Diga um valor em reais.');
                    isValid = false;
                } else {
                    value = String(value);
                }
                break;

            case 'status':
                if (matchAny(text, ['ativo', 'act', 'sim', 'yes'])) {
                    value = 'ativo';
                } else if (matchAny(text, ['esgotado', 'vazio', 'zero'])) {
                    value = 'esgotado';
                } else {
                    speak('Diga ativo ou esgotado.');
                    isValid = false;
                }
                break;

            // Campos de Pressão
            case 'cilindro_id':
                value = parseCodigo(text);
                if (!value || !value.match(/^CIL-\d{3}$/)) {
                    speak('Código inválido. Diga o código do cilindro, como zero zero um.');
                    isValid = false;
                }
                break;

            case 'pressao':
                value = parseNumero(text);
                if (!value || value < 0 || value > 300) {
                    speak('Pressão inválida. Diga um número de 0 a 300.');
                    isValid = false;
                } else {
                    value = String(value);
                }
                break;

            case 'temperatura':
                value = parseNumero(text);
                if (value === null || value < -50 || value > 100) {
                    speak('Temperatura inválida. Diga um número de menos 50 a 100.');
                    isValid = false;
                } else {
                    value = String(value);
                }
                break;

            case 'hora':
                value = parseHora(text);
                if (!value) {
                    speak('Hora inválida. Diga a hora no formato hora minuto.');
                    isValid = false;
                }
                break;

            // Campos de Elemento
            case 'nome':
                value = text.trim();
                if (!value || value.length < 2) {
                    speak('Nome inválido. Diga o nome do elemento.');
                    isValid = false;
                } else {
                    // Normalizar primeira letra maiúscula
                    value = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
                }
                break;

            case 'consumo_lpm':
                value = parseNumero(text);
                if (!value || value <= 0) {
                    speak('Consumo inválido. Diga um número positivo.');
                    isValid = false;
                } else {
                    value = String(value);
                }
                break;

            // Campos de Amostra
            case 'tempo_chama':
                value = parseTempoChama(text);
                if (!value) {
                    speak('Tempo inválido. Diga no formato hora minuto segundo.');
                    isValid = false;
                }
                break;

            case 'elemento_id':
                value = text.trim();
                if (!value || value.length < 2) {
                    speak('Nome inválido. Diga o nome do elemento.');
                    isValid = false;
                } else {
                    value = value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
                }
                break;

            case 'quantidade':
                value = parseNumero(text);
                if (!value || value < 1 || value > 1000) {
                    speak('Quantidade inválida. Diga um número de 1 a 1000.');
                    isValid = false;
                } else {
                    value = String(value);
                }
                break;
        }

        if (isValid && value) {
            voiceState.data[step.field] = value;
            voiceState.retries = 0;
            console.log('[VOICE] Coletado:', step.field, '=', value);
            updateDataPreview();

            // Próximo passo
            voiceState.currentStep++;

            if (voiceState.currentStep >= currentSteps.length) {
                // Ir para confirmação
                const summary = getConfirmationSummary();
                speak(summary + '. Confirma?');
                transitionTo('CONFIRMING');
            } else {
                // Próxima pergunta
                speak('Ok. ' + currentSteps[voiceState.currentStep].prompt);
            }
        } else {
            // Incrementar retries
            voiceState.retries++;
            console.log('[VOICE] Tentativa falhauda:', voiceState.retries);

            if (voiceState.retries >= voiceState.maxRetries) {
                speak('Muitas tentativas. Vamos recomeçar. ' + currentSteps[0].prompt);
                voiceState.currentStep = 0;
                voiceState.data = { ...defaultValues[voiceState.intent] };
                voiceState.retries = 0;
                transitionTo('COLLECTING');
            }
        }

        updateUI();
    }

    // ==================== BUSCAR IDs ====================
    async function buscarIdPorCodigo(codigo) {
        try {
            const response = await fetch('/api/buscar-codigo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codigo: codigo })
            });
            const result = await response.json();
            if (result.id) {
                return result.id;
            }
            return null;
        } catch (e) {
            console.error('[VOICE] Erro ao buscar ID do cilindro:', e);
            return null;
        }
    }

    async function buscarIdPorNomeElemento(nome) {
        try {
            const response = await fetch('/api/buscar-elemento', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nome: nome })
            });
            const result = await response.json();
            if (result.id) {
                return result.id;
            }
            return null;
        } catch (e) {
            console.error('[VOICE] Erro ao buscar ID do elemento:', e);
            return null;
        }
    }

    // ==================== EXECUÇÃO NO BANCO ====================
    async function executeInsert() {
        const intent = voiceState.intent;
        speak('Salvando ' + intent + '...');

        const data = new URLSearchParams();
        let endpoint = '/cilindros';
        let successMessage = '';

        if (intent === 'cilindro') {
            data.append('codigo', voiceState.data.codigo);
            data.append('data_compra', voiceState.data.data_compra);
            data.append('data_inicio_consumo', '');
            data.append('gas_kg', voiceState.data.gas_kg || '1.0');
            data.append('custo', voiceState.data.custo || '290.00');
            data.append('status', voiceState.data.status || 'ativo');
            data.append('action', 'create');
            endpoint = '/cilindros';
            successMessage = 'Cilindro ' + voiceState.data.codigo + ' salvo com sucesso!';
        } else if (intent === 'pressao') {
            // Buscar ID do cilindro pelo código via API
            const cilindroId = await buscarIdPorCodigo(voiceState.data.cilindro_id);
            if (!cilindroId) {
                speak('Cilindro não encontrado. Verifique o código.', false);
                voiceState.state = 'CONFIRMING';
                updateUI();
                return;
            }

            data.append('cilindro_id', cilindroId);
            data.append('pressao', voiceState.data.pressao || '0');
            data.append('temperatura', voiceState.data.temperatura || '25');
            data.append('data', voiceState.data.data || '');
            data.append('hora', voiceState.data.hora || '00:00');
            data.append('action', 'create');
            endpoint = '/pressoes';
            successMessage = 'Pressão registrada com sucesso!';
        } else if (intent === 'elemento') {
            data.append('nome', voiceState.data.nome || '');
            data.append('consumo_lpm', voiceState.data.consumo_lpm || '0');
            data.append('action', 'create');
            endpoint = '/elementos';
            successMessage = 'Elemento ' + voiceState.data.nome + ' salvo com sucesso!';
        } else if (intent === 'leitura') {
            // Buscar ID do cilindro pelo código via API
            const cilindroId = await buscarIdPorCodigo(voiceState.data.cilindro_id);
            if (!cilindroId) {
                speak('Cilindro não encontrado. Verifique o código.', false);
                voiceState.state = 'CONFIRMING';
                updateUI();
                return;
            }

            // Buscar ID do elemento pelo nome via API
            const elementoId = await buscarIdPorNomeElemento(voiceState.data.elemento_id);
            if (!elementoId) {
                speak('Elemento não encontrado. Verifique o nome.', false);
                voiceState.state = 'CONFIRMING';
                updateUI();
                return;
            }

            // Formatar hora como HH:MM:SS
            const hora = (voiceState.data.hora || '00').padStart(2, '0');
            const minuto = (voiceState.data.minuto || '00').padStart(2, '0');
            const segundo = (voiceState.data.segundo || '00').padStart(2, '0');
            const tempoChama = hora + ':' + minuto + ':' + segundo;

            data.append('data', voiceState.data.data || '');
            data.append('hora', hora);
            data.append('minuto', minuto);
            data.append('segundo', segundo);
            data.append('cilindro_id', cilindroId);
            data.append('elemento_id', elementoId);
            data.append('quantidade', voiceState.data.quantidade || '1');
            data.append('action', 'create');
            endpoint = '/leituras';
            successMessage = 'Leitura registrada com sucesso!';
        }

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRF-Token': getCsrfToken()
                },
                body: data.toString()
            });

            if (response.ok) {
                speak(successMessage);
                transitionTo('FEEDBACK');
                setTimeout(() => {
                    resetState();
                    speak('O que mais deseja fazer? Diga cilindro, pressão, elemento ou leitura.');
                }, 2000);
            } else {
                const error = await response.json();
                speak('Erro ao salvar. ' + (error.message || 'Tente novamente.'), false);
                voiceState.state = 'CONFIRMING';
            }
        } catch (e) {
            console.error('[VOICE] Erro:', e);
            speak('Erro de conexão. Tente novamente.', false);
            voiceState.state = 'CONFIRMING';
        }

        updateUI();
    }

    // ==================== HELPERS ====================
    function matchAny(text, patterns) {
        return patterns.some(p => text.includes(p));
    }

    function parseCodigo(text) {
        // Converter números escritos para número
        const num = parseNumero(text);
        if (num) {
            return 'CIL-' + String(num).padStart(3, '0');
        }
        
        // Se já tem CIL-, usar direto
        if (text.match(/cil-?\d/)) {
            const nums = text.replace(/cil-?/g, '');
            const n = parseInt(nums);
            if (n) return 'CIL-' + String(n).padStart(3, '0');
        }
        
        return null;
    }

    function parseNumero(text) {
        const numeros = {
            'zero': 0, 'um': 1, 'uma': 1, 'dois': 2, 'duas': 2, 'três': 3, 'tres': 3,
            'quatro': 4, 'cinco': 5, 'seis': 6, 'sete': 7, 'oito': 8, 'nove': 9,
            'dez': 10, 'onze': 11, 'doze': 12, 'treze': 13, 'quatorze': 14, 'quinze': 15,
            'dezasseis': 16, 'dezessete': 17, 'dezoito': 18, 'dezenove': 19,
            'vinte': 20, 'trinta': 30, 'quarenta': 40, 'cinquenta': 50,
            'cem': 100, 'mil': 1000
        };

        // Normalizar texto
        text = text.toLowerCase().trim();

        // Verificar decimais: "meio", "meia", "meia volta", "meia libra", "ponto cinco", "vírgula cinco"
        if (text.includes('meio') || text.includes('meia')) {
            // Tentar extrair parte inteira antes
            const antes = text.replace(/meio|meia/gi, '').trim();
            if (antes === '' || antes === 'um' || antes === 'uma') {
                return 0.5;
            }
            const parteInteira = parseNumero(antes);
            if (parteInteira !== null) return parteInteira + 0.5;
            return 0.5;
        }

        // Verificar decimais com "ponto" ou "vírgula"
        const decimalMatch = text.match(/(.+?)(ponto|virgula|vírgula)\s*(\w+)/);
        if (decimalMatch) {
            const parteInteira = parseNumero(decimalMatch[1].trim());
            const parteDecimal = numeros[decimalMatch[3]] || parseInt(decimalMatch[3]);
            if (parteInteira !== null && parteDecimal !== null && parteDecimal < 10) {
                return parteInteira + (parteDecimal / 10);
            }
        }

        // Verificar números compostos com "e" (ex: "vinte e um", "trinta e cinco")
        const match = text.match(/^(\w+)\s*e\s*(\w+)$/);
        if (match) {
            const a = numeros[match[1]];
            const b = numeros[match[2]];
            if (a !== undefined && b !== undefined && a < 100) return a + b;
        }

        // Verificar centenas compostas (ex: "cento e vinte", "duzentos e cinqüenta")
        const centenaMatch = text.match(/(cem|duzentos|trezentos|quatrocentos|quinhentos|seiscentos|setecentos|oitocentos|novecentos)\s*(e\s*(\w+))?/);
        if (centenaMatch) {
            const base = numeros[centenaMatch[1]];
            if (base !== undefined) {
                if (centenaMatch[3]) {
                    const dezena = numeros[centenaMatch[3]];
                    if (dezena !== undefined) return base + dezena;
                }
                return base;
            }
        }

        // Verificar dezenas com единицы (ex: "vinte um" sem "e")
        const dezenaUnidade = text.match(/^(vinte|trinta|quarenta|cinquenta)\s+(\w+)$/);
        if (dezenaUnidade) {
            const d = numeros[dezenaUnidade[1]];
            const u = numeros[dezenaUnidade[2]];
            if (d !== undefined && u !== undefined) return d + u;
        }

        // Verificar "mil" composto (ex: "mil e duzentos")
        const milMatch = text.match(/^(mil)\s*(e\s*(\w+))?/);
        if (milMatch) {
            if (milMatch[3]) {
                const valor = numeros[milMatch[3]];
                if (valor !== undefined) return valor;
            }
            return 1000;
        }

        // Número direto (dígitos)
        const direct = parseInt(text.replace(/[^\d]/g, ''));
        if (!isNaN(direct) && direct > 0) return direct;

        // Número por extenso direto
        return numeros[text] || null;
    }

    function parseData(text) {
        // Formato attendu: dia mês ano
        // Ex: "quinze de janeiro de dois mil e vinte quatro"
        const meses = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'marco': '03',
            'abril': '04', 'maio': '05', 'junho': '06', 'julho': '07',
            'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
        };

        // Tentar extrair dia, mês, ano
        const dia = parseNumero(text);
        let ano = new Date().getFullYear();

        // Procurar mês no texto
        for (const [mes, num] of Object.entries(meses)) {
            if (text.includes(mes)) {
                // Procurar ano depois do mês
                const anoMatch = text.match(/(dois\s+mil|dos\s+mil|dois mil|\d{4})/);
                if (anoMatch) {
                    const anoStr = anoMatch[1].replace(/\s+/g, '');
                    if (anoStr === 'doismil' || anoStr === 'dosmil' || anoStr === 'dois mil') {
                        ano = 2000;
                    } else if (!isNaN(parseInt(anoStr))) {
                        ano = parseInt(anoStr);
                    }
                }
                if (dia) {
                    const mesNum = meses[mes];
                    return String(ano) + '-' + mesNum + '-' + String(dia).padStart(2, '0');
                }
            }
        }

        return null;
    }

    function parseHora(text) {
        // Formato: hora minuto (ex: "quatorze e trinta", "14 30", "14h30")
        const horaMinuto = text.match(/(\d+)\s*(?:horas?|h)?\s*(?:e|\s)\s*(\d+)/);
        if (horaMinuto) {
            const hora = parseInt(horaMinuto[1]);
            const minuto = parseInt(horaMinuto[2]);
            if (hora >= 0 && hora <= 23 && minuto >= 0 && minuto <= 59) {
                return String(hora).padStart(2, '0') + ':' + String(minuto).padStart(2, '0');
            }
        }

        // Apenas hora
        const horaOnly = parseNumero(text);
        if (horaOnly !== null && horaOnly >= 0 && horaOnly <= 23) {
            return String(horaOnly).padStart(2, '0') + ':00';
        }

        return null;
    }

    function parseTempoChama(text) {
        // Formato: hora minuto segundo (ex: "1 hora 30 minutos 45 segundos")
        const parts = text.toLowerCase();

        let hora = 0, minuto = 0, segundo = 0;

        // Procurar hora
        const horaMatch = parts.match(/(\d+)\s*(?:hora|horas|h)/);
        if (horaMatch) hora = parseInt(horaMatch[1]);

        // Procurar minuto
        const minutoMatch = parts.match(/(\d+)\s*(?:minuto|minutos|m(?:in)?)/);
        if (minutoMatch) minuto = parseInt(minutoMatch[1]);

        // Procurar segundo
        const segundoMatch = parts.match(/(\d+)\s*(?:segundo|segundos|s)/);
        if (segundoMatch) segundo = parseInt(segundoMatch[1]);

        // Se não encontrou nenhum, tentar extrair 3 números
        if (hora === 0 && minuto === 0 && segundo === 0) {
            const nums = parts.match(/\d+/g);
            if (nums && nums.length >= 2) {
                hora = parseInt(nums[0]) || 0;
                minuto = parseInt(nums[1]) || 0;
                segundo = parseInt(nums[2]) || 0;
            }
        }

        if (hora >= 0 && minuto >= 0 && segundo >= 0 && (hora + minuto + segundo) > 0) {
            return hora + ':' + String(minuto).padStart(2, '0') + ':' + String(segundo).padStart(2, '0');
        }

        return null;
    }

    function getConfirmationSummary() {
        const data = voiceState.data;
        const intent = voiceState.intent;

        if (intent === 'cilindro') {
            return 'Código ' + (data.codigo || '') + ', data ' + (data.data_compra || '') + ', ' + (data.gas_kg || '') + 'kg, ' + (data.custo || '') + 'reais, ' + (data.status || '');
        } else if (intent === 'pressao') {
            return 'Cilindro ' + (data.cilindro_id || '') + ', pressão ' + (data.pressao || '') + ' bar, temperatura ' + (data.temperatura || '') + ' graus';
        } else if (intent === 'elemento') {
            return 'Nome ' + (data.nome || '') + ', consumo ' + (data.consumo_lpm || '') + ' L/min';
        } else if (intent === 'leitura') {
            return 'Data ' + (data.data || '') + ', tempo ' + (data.tempo_chama || '') + ', cilindro ' + (data.cilindro_id || '') + ', elemento ' + (data.elemento_id || '');
        }
        return 'Dados coletados';
    }

    function updateDataPreview() {
        const container = document.getElementById('voice-collected-data');
        if (!container) return;

        const data = voiceState.data;
        const intent = voiceState.intent;
        let preview = '';

        if (intent === 'cilindro') {
            preview = 'Código: ' + (data.codigo || '-') + '<br>Data: ' + (data.data_compra || '-') +
                      '<br>Kg: ' + (data.gas_kg || '-') + '<br>Custo: R$' + (data.custo || '-') +
                      '<br>Status: ' + (data.status || '-');
        } else if (intent === 'pressao') {
            preview = 'Cilindro: ' + (data.cilindro_id || '-') + '<br>Pressão: ' + (data.pressao || '-') + ' bar' +
                      '<br>Temp: ' + (data.temperatura || '-') + '°C<br>Data: ' + (data.data || '-') +
                      '<br>Hora: ' + (data.hora || '-');
        } else if (intent === 'elemento') {
            preview = 'Nome: ' + (data.nome || '-') + '<br>Consumo: ' + (data.consumo_lpm || '-') + ' L/min';
        } else if (intent === 'leitura') {
            preview = 'Data: ' + (data.data || '-') + '<br>Tempo: ' + (data.tempo_chama || '-') +
                      '<br>Cilindro: ' + (data.cilindro_id || '-') + '<br>Elemento: ' + (data.elemento_id || '-') +
                      '<br>Qtd: ' + (data.quantidade || '-');
        } else {
            preview = 'Nenhum';
        }

        container.innerHTML = preview;
    }

    function getCsrfToken() {
        // Tentar encontrar input hidden com name="csrf_token"
        const csrfInput = document.querySelector('input[name="csrf_token"]');
        if (csrfInput) return csrfInput.value;
        
        // Tentar meta tag
        const token = document.querySelector('meta[name="csrf-token"]');
        if (token) return token.getContent();
        
        // Tentar cookie
        const cookieMatch = document.cookie.match(/csrf_token=([^;]+)/);
        if (cookieMatch) return cookieMatch[1];
        
        return '';
    }

    // ==================== STATE MACHINE ====================
    function transitionTo(newState, extraData) {
        voiceState.state = newState;
        if (extraData) {
            Object.assign(voiceState.data, extraData);
        }
        console.log('[VOICE] Estado:', voiceState.state);
        updateUI();

        if (newState === 'EXECUTE') {
            executeInsert();
        }
    }

    function resetState() {
        voiceState.state = 'IDLE';
        voiceState.intent = null;
        voiceState.data = {};
        voiceState.currentStep = 0;
        voiceState.confirmed = false;
        console.log('[VOICE] Estado resetado');
        updateUI();
    }

    // ==================== UI ====================
    function updateUI() {
        const statusEl = document.getElementById('voice-status');
        if (statusEl) {
            let statusText = voiceState.state;
            if (voiceState.speaking) statusText = 'Falando...';
            else if (voiceState.recognizing) statusText = 'Ouvindo...';
            else if (voiceState.state === 'IDLE') statusText = 'Aguardando';
            else if (voiceState.state === 'EXECUTE') statusText = 'Salvando...';
            statusEl.textContent = statusText;
        }

        // Atualizar estado visual
        const stateEl = document.getElementById('voice-state');
        if (stateEl) {
            stateEl.textContent = voiceState.state;
        }

        // Atualizar passo atual e barra de progresso
        const stepEl = document.getElementById('voice-step-name');
        const progressBar = document.getElementById('voice-progress-bar');
        const currentSteps = intentSteps[voiceState.intent] || cilindroSteps;

        if (stepEl) {
            if (voiceState.state === 'IDLE') {
                stepEl.textContent = 'Início';
            } else if (voiceState.state === 'COLLECTING' && currentSteps[voiceState.currentStep]) {
                const step = currentSteps[voiceState.currentStep];
                stepEl.textContent = step.field + ' (' + (voiceState.currentStep + 1) + '/' + currentSteps.length + ')';
            } else if (voiceState.state === 'CONFIRMING') {
                stepEl.textContent = 'Confirmação';
            } else if (voiceState.state === 'EXECUTE' || voiceState.state === 'FEEDBACK') {
                stepEl.textContent = 'Concluindo...';
            } else {
                stepEl.textContent = voiceState.state;
            }
        }

        // Atualizar barra de progresso
        if (progressBar) {
            let progress = 0;
            if (voiceState.state === 'COLLECTING') {
                progress = ((voiceState.currentStep + 1) / currentSteps.length) * 100;
            } else if (voiceState.state === 'CONFIRMING') {
                progress = 100;
            } else if (voiceState.state === 'EXECUTE' || voiceState.state === 'FEEDBACK') {
                progress = 100;
            }
            progressBar.style.width = progress + '%';
        }

        // Atualizar hint
        const hintEl = document.getElementById('voice-hint');
        if (hintEl) {
            if (voiceState.state === 'IDLE') hintEl.textContent = 'Clique no microfone para falar';
            else if (voiceState.recognizing) hintEl.textContent = 'Fale agora...';
            else if (voiceState.speaking) hintEl.textContent = 'Ouvindo...';
            else if (voiceState.state === 'COLLECTING') hintEl.textContent = getHint();
            else if (voiceState.state === 'CONFIRMING') hintEl.textContent = 'Diga sim ou não';
            else hintEl.textContent = voiceState.state;
        }

        // Atualizar campo de texto (fallback)
        const textInput = document.getElementById('voice-text-input');
        if (textInput) {
            textInput.placeholder = getPlaceholder();
        }

        // Atualizar botão
        const micBtn = document.getElementById('voice-mic-btn');
        if (micBtn) {
            micBtn.disabled = voiceState.speaking;
            if (voiceState.recognizing) {
                micBtn.classList.add('recording');
            } else {
                micBtn.classList.remove('recording');
            }
        }
    }

    function getHint() {
        const currentSteps = intentSteps[voiceState.intent] || cilindroSteps;
        if (voiceState.state === 'COLLECTING' && currentSteps[voiceState.currentStep]) {
            const step = currentSteps[voiceState.currentStep];
            switch (step.field) {
                case 'codigo':
                case 'cilindro_id':
                    // Mostrar primeiro cilindro do usuário como exemplo
                    if (userCilindros.length > 0) {
                        return 'Exemplo: ' + userCilindros[0].codigo;
                    }
                    return 'Diga: zero zero um';
                case 'data_compra':
                case 'data':
                    return 'Diga: quinze de janeiro';
                case 'gas_kg':
                    return 'Diga: um quilo';
                case 'custo':
                    return 'Diga: duzentos e noventa';
                case 'status':
                    return 'Diga: ativo ou esgotado';
                case 'pressao':
                    return 'Diga: duzentos';
                case 'temperatura':
                    return 'Diga: vinte e cinco';
                case 'hora':
                    return 'Diga: quatorze e trinta';
                case 'nome':
                case 'elemento_id':
                    // Mostrar primeiro elemento do usuário como exemplo
                    if (userElementos.length > 0) {
                        return 'Exemplo: ' + userElementos[0].nome;
                    }
                    return 'Diga: Ferro';
                case 'consumo_lpm':
                    return 'Diga: ponto cinco';
                case 'tempo_chama':
                    return 'Diga: uma hora trinta';
            case 'quantidade':
                    return 'Diga: um';
            }
        }
        return 'Aguardando...';
    }

    function getPlaceholder() {
        const currentSteps = intentSteps[voiceState.intent] || cilindroSteps;
        switch (voiceState.state) {
            case 'IDLE': return 'Digite "cilindro" para iniciar';
            case 'INTENT': return 'Entendido. Continuando...';
            case 'COLLECTING':
                const step = currentSteps[voiceState.currentStep];
                return step ? step.prompt : '';
            case 'CONFIRMING': return 'Diga "sim" para confirmar';
            case 'EXECUTE': return 'Salvando...';
            case 'FEEDBACK': return 'Concluído!';
            default: return 'Aguardando...';
        }
    }

    // ==================== CARREGAR DADOS DO USUÁRIO ====================
    let userCilindros = [];
    let userElementos = [];

    async function loadUserData() {
        try {
            const response = await fetch('/api/dados-usuario');
            if (response.ok) {
                const data = await response.json();
                userCilindros = data.cilindros || [];
                userElementos = data.elementos || [];
                updateQuickSelectButtons();
                console.log('[VOICE] Dados do usuário carregados:', userCilindros.length, 'cilindros,', userElementos.length, 'elementos');
            }
        } catch (e) {
            console.error('[VOICE] Erro ao carregar dados do usuário:', e);
        }
    }

    function updateQuickSelectButtons() {
        const container = document.getElementById('voice-quick-buttons');
        if (!container) return;

        // Manter os botões fixos (opções de entidade, sim/não, cancelar)
        const fixedButtons = container.querySelectorAll('.quick-select[data-value="cilindro"], .quick-select[data-value="pressão"], .quick-select[data-value="elemento"], .quick-select[data-value="leitura"], .quick-select[data-value="ativo"], .quick-select[data-value="esgotado"], .quick-select[data-value="sim"], .quick-select[data-value="não"], .quick-select[data-value="cancelar"]');
        
        // Adicionar botões de cilindro
        userCilindros.forEach(cil => {
            if (!container.querySelector(`.quick-select[data-value="cil-${cil.codigo}"]`)) {
                const btn = document.createElement('button');
                btn.className = 'btn btn-sm btn-outline-dark quick-select';
                btn.setAttribute('data-value', 'cil-' + cil.codigo);
                btn.textContent = cil.codigo;
                btn.title = 'Código do cilindro';
                container.appendChild(btn);
                
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const value = this.getAttribute('data-value').replace('cil-', '');
                    preventAutoRecognition = true;
                    voiceState.recognizing = false;
                    addToHistory('Você', value);
                    processInput(value, 1.0, true);
                });
            }
        });

        // Adicionar botões de elemento
        userElementos.forEach(elem => {
            if (!container.querySelector(`.quick-select[data-value="elem-${elem.nome}"]`)) {
                const btn = document.createElement('button');
                btn.className = 'btn btn-sm btn-outline-info quick-select';
                btn.setAttribute('data-value', 'elem-' + elem.nome);
                btn.textContent = elem.nome.substring(0, 8);
                btn.title = 'Elemento: ' + elem.nome;
                container.appendChild(btn);
                
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const value = this.getAttribute('data-value').replace('elem-', '');
                    preventAutoRecognition = true;
                    voiceState.recognizing = false;
                    addToHistory('Você', value);
                    processInput(value, 1.0, true);
                });
            }
        });
    }

    // ==================== INICIALIZAÇÃO ====================
    function init() {
        console.log('[VOICE] Inicializando...');

        if (!isSpeechSupported()) {
            console.warn('[VOICE] Web Speech API não suportado');
            showUnsupportedAlert();
            return;
        }

        recognition = initRecognition();
        if (!recognition) {
            console.warn('[VOICE] Falha ao inicializar reconhecimento');
            return;
        }

        // Carregar dados do usuário para quick-select dinâmico
        loadUserData();

        console.log('[VOICE] Inicializado com sucesso');
        updateUI();

        // Botão do microfone
        document.getElementById('voice-mic-btn')?.addEventListener('click', toggleVoice);
        
        // Botão de texto
        document.getElementById('voice-text-btn')?.addEventListener('click', submitText);
        document.getElementById('voice-text-input')?.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') submitText();
        });

        // Botão fechar
        document.getElementById('voice-close-btn')?.addEventListener('click', closeModal);

        // Botão iniciar conversa
        document.getElementById('voice-start-btn')?.addEventListener('click', startConversation);

        // Botão reset
        document.getElementById('voice-reset-btn')?.addEventListener('click', function() {
            resetState();
            speak('Conversa reiniciada. O que deseja fazer?');
        });

        // Botões de seleção rápida
        document.querySelectorAll('.quick-select').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const value = this.getAttribute('data-value');
                console.log('[VOICE] Quick select:', value);

                // IMPORTANTE: Não iniciar reconhecimento automático após quick-select
                // Isso evita que o sistema "ouça" duas vezes
                preventAutoRecognition = true;

                // Resetar estado de reconhecimento antes de processar
                voiceState.recognizing = false;

                addToHistory('Você', value);
                processInput(value.toLowerCase(), 1.0, true);

                console.log('[VOICE] Quick select processado, auto-reconhecimento bloqueado');
            });
        });
    }

    function showUnsupportedAlert() {
        const alert = document.createElement('div');
        alert.className = 'alert alert-warning position-fixed bottom-0 end-0 m-3';
        alert.innerHTML = '<i class="bi bi-exclamation-triangle"></i> ' +
            'Navegador não suporta reconhecimento de voz. Use Chrome ou Edge.';
        document.body.appendChild(alert);
    }

    // ==================== EVENTOS ====================
    function toggleVoice() {
        if (!recognition) {
            speak('Navegador não suporta. Use Chrome ou Edge.');
            return;
        }

        if (voiceState.speaking) {
            synthesis.cancel();
            return;
        }

        if (voiceState.recognizing) {
            stopRecognition();
        } else {
            if (voiceState.state === 'IDLE') {
                // O onend do speak já vai iniciar o reconhecimento automaticamente
                speak('Olá! O que deseja registrar?', true);
            } else {
                startRecognition();
            }
        }
    }

    function startConversation() {
        if (!recognition) {
            speak('Navegador não suporta. Use Chrome ou Edge.', false);
            return;
        }

        voiceState.state = 'IDLE';
        // O onend do speak já vai iniciar o reconhecimento automaticamente
        speak('Olá! O que deseja registrar?', true);
    }

    function submitText() {
        const input = document.getElementById('voice-text-input');
        const text = input?.value?.toLowerCase().trim();
        if (!text) return;

        console.log('[VOICE] Texto:', text);
        processInput(text, 1.0);
        input.value = '';
    }

    function closeModal() {
        stopRecognition();
        synthesis.cancel();
        resetState();
        
        const modal = document.getElementById('voice-modal');
        if (modal) modal.classList.remove('show');
    }

    // Inicializar quando DOM pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expor funções globais
    window.toggleVoice = toggleVoice;
    window.submitText = submitText;
    window.startConversation = startConversation;
    window.closeVoiceModal = closeModal;

})();