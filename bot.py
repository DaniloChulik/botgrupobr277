import json
import requests
import pytz
import random
import re
from datetime import datetime
from urllib.parse import quote

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Chaves de API
TOKEN_TELEGRAM = '7656877931AAFPzQRuipLfAut9IlhULXpZr0azTI-lSXk'
API_KEY_GOOGLE_MAPS = 'AIzaSyBXZzcP64u12c5f3etphHI1a0CnNwTQ5Kk'

estado_para_sigla = {
    State of Acre AC, State of Alagoas AL, State of Amapá AP, State of Amazonas AM,
    State of Bahia BA, State of Ceará CE, State of Espírito Santo ES, State of Goiás GO,
    State of Maranhão MA, State of Mato Grosso MT, State of Mato Grosso do Sul MS,
    State of Minas Gerais MG, State of Pará PA, State of Paraíba PB, State of Paraná PR,
    State of Pernambuco PE, State of Piauí PI, State of Rio de Janeiro RJ,
    State of Rio Grande do Norte RN, State of Rio Grande do Sul RS, State of Rondônia RO,
    State of Roraima RR, State of Santa Catarina SC, State of São Paulo SP,
    State of Sergipe SE, State of Tocantins TO, Federal District DF, Brazil Brasil
}

mensagens_seguranca = [
    🚗 Use sempre o cinto de segurança.,
    🚧 Mantenha distância segura do veículo à frente.,
    📵 Celular e direção não combinam.,
    ⚠️ Respeite os limites de velocidade.,
    🛑 Pare sempre na faixa de pedestres.,
    🚦 Sinal vermelho significa pare!,
    🔍 Faça revisões periódicas no seu veículo.,
    🌧️ Em dias de chuva, reduza a velocidade.,
    🕒 Respeite o tempo de descanso na direção.,
    🍺 Se beber, não dirija.,
    🚘 Olhe sempre os espelhos retrovisores.,
    🚚 Cuidado ao ultrapassar caminhões.,
    🛣️ Atenção redobrada em rodovias.,
    🧯 Verifique os itens de segurança do veículo.,
    🛞 Calibre os pneus regularmente.,
    🔧 Faça manutenção preventiva do carro.,
    📵 Evite distrações enquanto dirige.,
    🚙 Ligue os faróis, mesmo de dia, na estrada.,
    🚸 Redobre a atenção em áreas escolares.,
    🦺 Use triângulo de sinalização em emergências.,
    🚫 Não force ultrapassagens perigosas.,
    🛑 Respeite a sinalização da via.,
    ⚙️ Engate a marcha ao estacionar em descidas.,
    📛 Dirija com atenção perto de ciclistas.,
    🛑 Nunca pare em cima da faixa de pedestres.,
    🚥 Use seta para indicar suas manobras.,
    👀 Mantenha os olhos atentos ao trânsito.,
    🗺️ Planeje sua rota antes de sair.,
    🚦 Dê preferência à vida, não ao tempo.,
    🎧 Evite usar fones de ouvido ao dirigir.,
    📵 Nada de redes sociais ao volante.,
    🏁 Respeite os limites da via.,
    🕯️ Ligue o pisca-alerta apenas quando necessário.,
    💤 Evite dirigir com sono.,
    🚷 Não bloqueie cruzamentos.,
    📐 Regule os retrovisores corretamente.,
    🔋 Verifique a bateria antes de viajar.,
    🧊 Cuidado com pistas molhadas ou escorregadias.,
    🔦 Verifique as luzes do veículo.,
    🏍️ Use capacete ao pilotar motos.,
    🚳 Bicicleta também tem regras no trânsito.,
    🆘 Saiba acionar socorro em emergências.,
    🔄 Use a faixa da esquerda só para ultrapassagens.,
    🚛 Cuidado com pontos cegos de veículos grandes.,
    🗣️ Avise manobras com antecedência.,
    🚯 Não jogue lixo nas estradas.,
    🎯 Foco total no volante.,
    🚦 Trânsito seguro depende de todos.,
    ✅ Faça sua parte pela segurança no trânsito.,
    📢 Compartilhe boas práticas no trânsito.
]

def traduz_endereco(endereco)
    for termo, sigla in estado_para_sigla.items()
        endereco = endereco.replace(termo, sigla)
    return endereco

def traduz_duracao(texto)
    texto = texto.replace('hours', 'horas').replace('hour', 'hora')
    texto = texto.replace('and', 'e')
    texto = re.sub(r'bminsb', 'minutos', texto)
    texto = re.sub(r'bminb', 'minuto', texto)
    return texto

def extract_locations(text)
    text = text.lower()
    text = re.sub(r'[^ws]', '', text)
    words = text.split()
    origem = destino = None
    if 'para' in words
        idx = words.index('para')
        origem = ' '.join(words[idx])
        destino = ' '.join(words[idx + 1])
    elif len(words) = 2
        origem = words[0]
        destino = words[1]
    if origem
        origem = quote(origem + ', Brasil')
    if destino
        destino = quote(destino + ', Brasil')
    return origem, destino

def get_traffic_status(sem_trafego, com_trafego)
    diferenca = com_trafego - sem_trafego
    if diferenca  300
        return 🟢 Trânsito livre, Deslocamento rápido.
    elif diferenca  900
        return 🟡 Trânsito moderado, Leves retenções no trajeto.
    else
        return 🔴 Trânsito pesado, Retenções significativas. Considere rotas alternativas.

async def handle_message(update Update, context ContextTypes.DEFAULT_TYPE)
    if update.message is None or update.message.text is None
        return

    text = update.message.text.lower()
    origem, destino = extract_locations(text)

    if origem and destino
        try
            url = f'httpsmaps.googleapis.commapsapidirectionsjsonorigin={origem}&destination={destino}&mode=driving&departure_time=now&traffic_model=best_guess&region=br&key={API_KEY_GOOGLE_MAPS}'
            response = requests.get(url)
            data = json.loads(response.text)

            if 'routes' in data and len(data['routes'])  0 and data['status'] == 'OK'
                main_route = data['routes'][0]['legs'][0]
                alternative_routes = data['routes'][1] if len(data['routes'])  1 else []

                distance = main_route['distance']['text']
                duracao_sem_trafego_valor = main_route['duration']['value']
                duracao_com_trafego_valor = main_route.get('duration_in_traffic', main_route['duration'])['value']

                if duracao_com_trafego_valor = duracao_sem_trafego_valor
                    tempo_sem_trafego = traduz_duracao(main_route['duration']['text'])
                    tempo_com_trafego = traduz_duracao(main_route.get('duration_in_traffic', main_route['duration'])['text'])
                else
                    duracao_com_trafego_valor, duracao_sem_trafego_valor = duracao_sem_trafego_valor, duracao_com_trafego_valor
                    tempo_com_trafego = traduz_duracao(main_route['duration']['text'])
                    tempo_sem_trafego = traduz_duracao(main_route.get('duration_in_traffic', main_route['duration'])['text'])

                status, details = get_traffic_status(duracao_sem_trafego_valor, duracao_com_trafego_valor)

                rodovias = []
                incidentes = []

                for step in main_route['steps']
                    if 'html_instructions' in step
                        match = re.findall(r'BR-d+', step['html_instructions'])
                        for rod in match
                            if rod not in rodovias
                                rodovias.append(rod)
                    if 'maneuver' in step and step['maneuver'] in ['accident', 'construction']
                        incidentes.append(step['maneuver'])

                incidentes_texto = 
                if incidentes
                    tipos = set(incidentes)
                    incidentes_texto = n🚨 Incidente(s) no trajeto  + , .join(tipos).capitalize()

                pedagio_info = 💰 Sem pedágios conhecidos neste trajeto.
                if rodovias
                    pedagio_info = 💰 Pedágio neste trajeto + ''.join(fn• {rodovia} for rodovia in rodovias)

                maps_link = fhttpswww.google.commapsdirapi=1&origin={quote(origem)}&destination={quote(destino)}&travelmode=driving

                brasilia_tz = pytz.timezone('AmericaSao_Paulo')
                current_time = datetime.now(brasilia_tz).strftime('%H%M - %d%m%Y')
                origem_br = traduz_endereco(main_route['start_address'])
                destino_br = traduz_endereco(main_route['end_address'])
                mensagem_aleatoria = random.choice(mensagens_seguranca)

                message = fATUALIZAÇÃOn{current_time}nn🛣️ Origem {origem_br}n🏁 Destino {destino_br}nnDistância {distance}nCom Trânsito {tempo_com_trafego}nn{status} - {details}{incidentes_texto}nn{pedagio_info}nnConfira no GPS ou rota alternativan🔗 [Abrir no Google Maps]({maps_link})nn{mensagem_aleatoria}nn_Informações GRUPO BR 277_

                if alternative_routes
                    message += nn🚗 Rotas alternativas
                    for i, route in enumerate(alternative_routes[2], 1)
                        alt_leg = route['legs'][0]
                        alt_distance = alt_leg['distance']['text']
                        alt_duration = traduz_duracao(alt_leg.get('duration_in_traffic', alt_leg['duration'])['text'])
                        message += fn➡️ Alternativa {i} {alt_distance}  {alt_duration}

                await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')

        except Exception as e
            await context.bot.send_message(chat_id=update.effective_chat.id, text='⚠️ Ocorreu um erro ao buscar as informações. Tente novamente em instantes.')

if __name__ == '__main__'
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print(Bot iniciado...)
    app.run_polling()


pythonbrprint(Bot funcionando!)