import discord
import random
import os
from discord.ext import commands
import pandas as pd
import math

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '.', description="type .help for available commands", intents = intents,help_command=None)
df = pd.read_csv('data.csv',index_col=0)
teams = len(df)
asked = False
#add aliases to commands
#Too much initial credits
#IQ equation too steep
#Flora cap 100
#credits exhaust message, stop transactions
#fix resource bought message
#show population increase/decrease in embed

size = {1:"Small", 2:"Medium", 3:"Large"} #large is good
distance = {2:"Close", 3:"Ideal", 1:"Far"} #ideal is good
mass = {1:"Light", 2:"Medium", 3:"Heavy"} 

d_era = {
    1:"Ancient",
    2:"Medieval",
    3:"Industrial",
    4:"Information",
    5:"Future"}

crisis_aliases={
    'floods':'Floods',
    'drought':'Droughts',
    'famine':'Famine',
    'tsunami':'Tsunami',
    'cyclone':'Cyclone',
    'earthquake':'Earthquake',
    'fire':'Forest Fires',
    'plague':'Plague',
    'fuel':'Fuel Shortage',
    'wars':'Great Wars',
    'warming':'Global Warming',
    'watershortage':'Water Shortage',
    'corona':'Corona',
    'ebola':'Ebola',
    'flare':'Solar Flare',
    'nuclear':'Nuclear Disaster',
    'ozone':'Ozone Depletion',
    'ai':'AI Coup'}

res_aliases={
    'seeds':'Seed Pods',
    'oxygen':'Oxygen',
    'co2':'Carbon Dioxide',
    'pollute':'Pollutants',
    'water':'Water',
    'land':'Land',
    'temp':'Temperature',
    'population':'Population',
    'biomes':'Biomes',
    'factory':'Factory(s)',
    'farm':'Farm(s)'}

initial_values={
    'era':1,
    'story':0,
    'size':0,
    'distance':0,
    'mass':0,
    'mult':0,
    'si':0,
    'di':0,
    'credits':10000.0,
    'population':1000,
    'change':0,
    'iq':10.0,
    'pdensity':2,
    'oxygen':25.0,
    'co2':0,
    'pollute':0,
    'water':0,
    'land':0,
    'temp':0,
    'biomes':0,
    'farm':0,
    'factory':0,
    'mine':0,
    'ai':0,
    'satellite':0,
    'dyson':0}

def initialise():
    #Active parameter chart
    water = {1:50, 2:60, 3:70}
    temp = {2:17 , 3:14 , 1:11}
    #Passive parameters
    with open('parameters.csv','w') as para_file:
            para_file.write('turn,1')
            para_file.close()

    for i in range(len(df.index)):
        for res in range(2,len(df.keys())):
            df.iloc[i,res]=0
        initial_values['size']=random.choice(list(size.keys()))
        initial_values['distance']=random.choice(list(distance.keys()))
        initial_values['mass']=initial_values['size'] 

        #Active parameters
        initial_values['water'] = water[initial_values['size']]
        initial_values['land'] = 100 - initial_values['water']
        initial_values['temp'] = temp[initial_values['distance']]

        si= round(0.000044*initial_values['water']*initial_values['land']*initial_values['oxygen']*(60-initial_values['oxygen']),2)
        initial_values['mult']=round(initial_values['water']/(120-initial_values['water']),2)
        
        #Initial resources
        initial_values['biomes']=random.randrange(40,60) #randomising flora and fauna diversity
        value_list=list(initial_values.values())
        
        for res in range(1,len(df.keys())):
            df.iloc[i,res]=value_list[res-1]
    df.to_csv('data.csv')

def crisis_for_era(i): 
    era=df.loc[i,'era']
    water=df.loc[i,'water']
    land=df.loc[i,'land']
    di=df.loc[i,'di']
    population=df.loc[i,'population']
    farm=df.loc[i,'farm']
    biomes=df.loc[i,'biomes']
    temp=df.loc[i,'temp']
    oxygen=df.loc[i,'oxygen']
    co2=df.loc[i,'co2']
    factory=df.loc[i,'factory']
    satellite=df.loc[i,'satellite']
    pollute=df.loc[i,'pollute']
    crisis='none'
    cf=pd.read_csv('crisis.csv')
    era_df=cf.loc[cf['era']==era]
    print(era_df)

    era_list=list(era_df['crisis'])
    print(era_list)
    if 'floods' in era_list and water < 40:
        era_list.remove('floods')
    if 'drought' in era_list and water > 30:
        era_list.remove('drought')
    if 'watershortage' in era_list and water > 40:
        era_list.remove('watershortage')
    if 'cyclone' in era_list and water < 50: 
        era_list.remove('cyclone')
    if 'tsunami' in era_list and water < 50:
        era_list.remove('tsunami')
    if 'ozone' in era_list and pollute < 50:
        era_list.remove('ozone')
    if 'warming' in era_list and (oxygen > 13 and co2 < 10):
        era_list.remove('warming')
    if 'famine' in era_list and (1000*farm/population > 1  and water > 35):
        era_list.remove('famine')
    
    chance = random.random()
    if chance < 1:
        crisis = random.choice(era_list)
    print(crisis)
    death=0
    if crisis!='none':
        print(float(era_df.loc[era_df['crisis']==crisis,'death']))
        death = int(int(population)*float(era_df.loc[era_df['crisis']==crisis,'death'])/100)
        population=int(population)-death
        for index in era_df.loc[era_df['crisis']==crisis].keys()[3:]:
            print(index, end=' ')
            df.loc[i,str(index)]=locals()[str(index)]*(1-float(era_df.loc[era_df['crisis']==crisis,index])/100)
    if crisis == 'flare':
        satellite = int(satellite*0.8)
    elif crisis == 'ai':
        factory = int(factory*1.2)
    elif crisis ==  'floods' or crisis == 'drought':
        farm = int(farm*0.9)

    df.loc[i,'population']=population
    df.loc[i,'farm']=farm
    df.loc[i,'factory']=factory
    df.loc[i,'satellite']=satellite
    '''df.loc[i,'water']=water
    df.loc[i,'land']=land
    df.loc[i,'di']=di
    df.loc[i,'flora']=flora
    df.loc[i,'temp']=temp'''
    return crisis,death

async def new_era(ctx, era):
    await ctx.send("Congratulations! Your civilization has progressed to " + d_era[era] + " era.")
    
    if era < 3:
        await ctx.send("You have uncovered a memory Cache.")
        message=""
        for line in open('./story'+str(era-1)+'1.txt',encoding='utf8'):
            message = message + line
        await ctx.send(message)
        message=""
        for line in open('./story'+str(era-1)+'1.txt',encoding='utf8'):
            message = message + line
        await ctx.send(message)
    elif era < 5:
        await ctx.send("Do you wish to dedicate some resources to excavate a possible artifact.\n'.story y' for yes and '.story n' for no")
        asked = True
    else:
        if df.loc[id,'story'] == 2:
            message=""
            for line in open('./story'+era+'.txt',encoding='utf8'):
                message = message + line
                await ctx.send(message)
            await ctx.send("Do you wish to dedicate some resources to excavate a possible artifact.\n'.story y' for yes and '.story n' for no")
            asked = True

@client.command()
async def story(ctx, answer):
    if asked == True:
        id = ctx.channel.id
        if df.loc[id,'era'] == 5 :
            if answer == 'yes' and df.loc[id,'story'] == 2:
                pass #add epilogue 1
            else:
                pass #add epilogue 2
        if answer == 'yes':
            df.loc[id,'story'] = df.loc[id,'story'] + 1

async def buy_list(ctx, era):
    res_file=open('resources.csv','r')
    embed = discord.Embed(title="Resource Buy List",color=discord.Colour.red(), description='Resources available')
    for line in res_file:
        lst=line.split(sep=',')
        if int(lst[era+1]):
            embed.add_field(name=str(lst[0])+' : '+str(float(lst[era+1])*float(df.loc[int(ctx.channel.id),'mult'])), value='Buy '+lst[1]+' '+res_aliases[lst[0]] ,inline=False)
    await ctx.send(embed=embed)

def buy_resource(id,resource,quantity):
    cred=0
    amount=0
    exhaust=0
    rf = pd.read_csv('mapping.csv')
    era=int(df.loc[id,'era'])
    with open('resources.csv') as resource_file:
        for row in resource_file:
            if row.split(sep=',')[0].lower()==resource.lower():
                cred=row.split(sep=',')[era+1]
                amount=row.split(sep=',')[1]
    if float(cred)==0:
        return False,exhaust
    else:
        updated_creds=df.loc[id,'credits']-int(quantity)*float(cred)*df.loc[id,'mult']
        if updated_creds<0:
            exhaust=1
        else:
            df.loc[id,'credits']=updated_creds
            if resource.lower() == 'seeds':
                seed = int(3*int(df.loc[id,'population'])/100 + float(df.loc[id,'si'])*10)
                df.loc[id,'population']=int(df.loc[id,'population']+int(quantity)*seed)
            else:
                df.loc[id,str(resource)]=df.loc[id,str(resource)]+int(quantity)*float(amount)
                di_i = int(quantity)*float(amount)/df.loc[id,str(resource)]
                df.loc[id,'di']=df.loc[id,'di']+round(di_i,2) 
            for index in rf.keys()[1:]:
                df.loc[id,index]=df.loc[id,index]+int(quantity)*float(rf.loc[rf['f']==resource,index])

        df.to_csv('data.csv')

        return True,exhaust

@client.command()
async def turn(ctx):
    if ctx.channel.id == 824221175995432961:
        asked = False
        turn=0
        with open('parameters.csv','r+') as para_file:
            turn=[row.split(sep=',')[1] for row in para_file]
            para_file.seek(0,os.SEEK_SET)
            para_file.write('turn,'+str(int(turn[0])+1))
            para_file.close()

        for i in range(teams):
            id = [int(x) for x in df.index][i]
            chan=client.get_channel(int(id))
            mess=await chan.get_partial_message(chan.last_message_id).fetch()
            cont=await client.get_context(mess)

            water=df.loc[id,'water']
            land=df.loc[id,'land']
            pollute=df.loc[id,'pollute']
            di=df.loc[id,'di']
            biomes=df.loc[id,'biomes']
            size_p=df.loc[id,'size']
            oxygen=df.loc[id,'oxygen']
            era=df.loc[id,'era']
            iq=10 + 240*(1-math.exp(-di*era))

            if iq>150:
                era=5
            elif iq>100:
                era=4
            elif iq>60:
                era=3
            elif iq>30:
                era=2
            #if df.loc[id,'era']!=era:
                #await new_era(cont,era)

            df.loc[id,'era']=era
            population=df.loc[id,'population']
            pdensity=int(iq/10+1)
            si= 0.00004*water*land*(1-pollute/100)*oxygen*(60-oxygen)
            pop_capacity=(pdensity-biomes/100)*land*int(size_p)*1000
            new_pop=int(population*si*0.03*(1-population/pop_capacity))
            df.loc[id,'change']=new_pop-population
            df.loc[id,'iq']=iq  
            df.loc[id,'population']=new_pop
            df.loc[id,'pdensity']=pdensity
            df.loc[id,'credits'] = df.loc[id,'credits'] + (si*di*(1.5**era))
            await cont.send(("Turn "+turn[0]+' started!'))
            crisis,death=crisis_for_era(id)
            #print(crisis,death)
            if crisis!='none':
                await cont.send('Your civilization is hit by '+crisis_aliases[crisis]+'.\nYou lost '+str(death)+' people.')
            await stats(cont)
            df.to_csv('data.csv')

@client.command()
async def buy(ctx,resource,quantity=1):
    team=ctx.channel.id
    unlocked,exhaust=buy_resource(team,resource,quantity)
    if unlocked:
        if not exhaust:
            await ctx.send(str(quantity)+' '+res_aliases[resource] + " successfully bought! \nPlease check your stats.")
        else:
            await ctx.send("You don\'t have the credits to perform this transaction. Kindly wait for the next turn.")
    else:
        await ctx.send("Resource not available.")
        

@client.command()
async def start(ctx):
    if ctx.channel.id == 824221175995432961:
        message=""
        for line in open('./start_message.txt',encoding='utf8'):
            message = message + line
        embed=discord.Embed(title='Prologue', 
            description = f'{message}',
            color = discord.Colour.red())
        await ctx.send(embed=embed)

        initialise()
        for i in range(teams):
            id = [int(x) for x in df.index][i]
            chan=client.get_channel(int(id))
            mess=await chan.get_partial_message(chan.last_message_id).fetch()
            cont=await client.get_context(mess)
            await stats(cont)

@client.command()
async def stats(ctx):
    id=ctx.channel.id
    era=int(df.loc[id,'era'])
    embed=discord.Embed(title='Stats',
        description = f"Your planet : {str(df.loc[id,'name'])}\n Current Era : { d_era[int(df.loc[id,'era'])]}\n Population : { float(df.loc[id,'population'])} ({'{:+}'.format(df.loc[id,'change'])}) \n Average IQ : { round(df.loc[id,'iq'],3)}\n Credits : {float(df.loc[id,'credits'])}\n"
                      f"-----------------------------------------------\n"
                      f"Resources\n"
                      f"-----------------------------------------------\n"
        ,color=discord.Colour.blue()
    )
    for i in list(df.loc[id].keys())[14:]:
        if float(df.loc[id,i])>0:    
            embed.add_field(name=res_aliases[i], value=float(df.loc[id,i]), inline=True)
    await ctx.send(embed=embed)
    await buy_list(ctx, era)

@client.command()
async def id(ctx):
    print("ID requested:", ctx.channel.id)
    print("Channel: ", ctx.channel.name)

'''@client.event
async def on_message(message):
    print(f'{message.author} sends',message.content)'''

@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")

@client.command()
async def reload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")

for filename in os.listdir('./cogs'):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client_id='NzczNDUzMDE5MzY2NDI0NTg2.X6JcQQ.JkIlfym8HiumdtgEuDt-zf3VnW0'
client.run(client_id)
