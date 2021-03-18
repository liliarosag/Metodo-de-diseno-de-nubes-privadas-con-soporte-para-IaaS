import time,sys,os,datetime,re,subprocess
from operator import itemgetter

##Estructura VALUE_LIST
#VALUE_LIST=('Unix time','Elapsed time','User','Status','Bytes recieved','Request type','URL','USER')

##Valores Iniciales
first=True

#Inroducir dentro de los parentesis todos los usuarios a evaluar ej: users = ["usr1","usr2",...,"usrn"]
users = ["ftgilberto.mg","ftclaudia.av"]

throughput_list=[]                            
delay_list=[]                                 
errors=[]
bienvenida='''Este documento contiene información recogida sobre el
experimento QoE/QoS llevada a cabo en la fecha %s.\n\n'''%time.strftime("%d/%m/%Y")
    
def main():
    with open(file_name) as f:
        text = f.read(30)
    timestamp1,timestamp2 = time_maker(text)
    for i in range(len(users)):
        throughput_list.append([])
        delay_list.append([])
        errors.append({})
    file=open(file_name,'r',encoding = "ISO-8859-1")
    #Separar linea por elementos
    for line in file:
        #print(float(line[:15]))
        if float(line[:15])>=timestamp1 and float(line[:15])<=timestamp2:
            value_list=line.split(' ')
            #Remover espacios en blanco innecesarios
            c=value_list.count('')
            for i in range(c): value_list.remove('')
            #Cálculo del throughput y delay de las peticiones validas por usuario, si es uno de los testados
            if value_list[7]in users :
                status=value_list[3].split('/')
                index=users.index(value_list[7])
                #if int(status[1])<400 #Aqui se toman como errores los codigos mayores de 400
                if int(status[1])>=100 and int(status[1])<400:#Aqui se toman como errores los codigos 000 tambien, elegir cual usar
                    try:
                        throughput=float(value_list[4])*8/float(value_list[1]) #Cant de (bytes reciv*8 )/elapsed time/1000
                        throughput_list[index].append(throughput)
                        delay = float(value_list[1])/1000
                        delay_list[index].append(delay)
                    except ZeroDivisionError:
                        pass
                
                else:
                    create_err_dict(value_list[3],index)
                
    make_file(int(timestamp1))
    file.close()
    print('Done!!!')
    if sys.platform == 'win32':
       subprocess.Popen(['start','%s.txt'%int(timestamp1)],shell=True)
    else:
        subprocess.Popen(['see','%s.txt'%int(timestamp1)])
#Crear archivo
def time_maker(text):
    global start_time
    match = re.search('[\d]{9,11}\.[\d]{1,5}',text)
    timestamp = datetime.datetime.fromtimestamp(float(match.group()))
    date = timestamp.strftime('%d/%m/%Y')
    print('This log file is from the day',date)
    start_time = input('Insert the time to start [hh:mm]: ')
    end_time = input('Insert the time to end [hh:mm]: ')
    st = "%s %s"%(date,start_time)
    et = "%s %s"%(date,end_time)
    
    try:
        st_obj = datetime.datetime.strptime(st,'%d/%m/%Y %H:%M')
        et_obj = datetime.datetime.strptime(et,'%d/%m/%Y %H:%M')
        tstamp1 = st_obj.timestamp()
        tstamp2 = et_obj.timestamp()
    except Exception as e:
        print('\n'+str(e).replace('%','').capitalize(),'\n')
        time_maker(text)
    return tstamp1,tstamp2
def make_file(timestamp):
    '''Método para estructurar el
       archivo del informe'''
    global first
    data=open('%s.txt'%timestamp,'w')
    for i in users:
        indice=users.index(i)
        avg_throu=prom(throughput_list[indice])
        avg_delay=prom(delay_list[indice])
        dictionary=errors[indice] #dicionario correspondiente a cada usuario
        v=list(dictionary.values())
        error=sum(v)
        if first:   #Mensaje de bienvenida si es la primera vez escribiendo el archivo                    
            first=False
            data.write(' '.center(67,'*')+'\n\n')
            data.write(bienvenida)
            horario = 'HORARIO\t%s'%datetime.datetime.fromtimestamp(timestamp)
            data.write(horario.center(70,' ')+'\n')
            data.write(' '.center(67,'*')+'\n')
            data.write('Users\t\t\t\tAvg Throughput(kb/s)\tAvg Delay(s)\n')
        data.write('\n'+users[indice]+'\t\t\t%0.2f\t\t\t%0.2f\n\nErrors: %d.\n'%(avg_throu,avg_delay,error))
        for key, values in sorted(dictionary.items(),key=itemgetter(1),reverse=True):
            data.write(str(key)+':'+str(values)+'\n')
        data.write('-'*65)
    data.close()
    return

def prom(data):
    try:
        prom=sum(data)/len(data)
    except ZeroDivisionError:
        prom=0
    return prom

def create_err_dict(status,index):
    '''Aqui agrego el código de error a uno diccionario
    con valor igual número de veces que ha aparecido'''
    dic=errors[index]    #dic es el dicionario correspondiente al usuario en la posicion
    if status in dic:    #index de la lista de usuarios 'users'
        dic[status]+=1
    else:
        dic[status]=1
        
if __name__=='__main__':
    try:
        file_name = sys.argv[1]
    except IndexError:
        file_name = 'access.log'
    if not os.path.exists(file_name):
        print('The file "access.log" is not located in the current working directory\nPlease copy the file in the current dir or pass the path to a different file in the command line')
        sys.exit(1)
    main()
