import json, random, math, time
import asyncio
from datetime import datetime, timedelta

class DocSession:

    def __init__(self, doc_urn):
        self.urn = doc_urn
        self.doc_id = doc_urn.split(':')[1]
        # self.duration_in_minutes = random.choice([5, 10, 15, 20, 25, 30]) # minutes
        self.duration_in_minutes = random.choice(cfg['session']['duration_in_minutes_choices']) # minutes
        _range = cfg['session']['max_users_range']
        self.max_users = random.randint(_range[0], _range[1])
        self.users = []
        for i in range(0, self.max_users):
            self.users.append(User(f"user:{self.doc_id}:{i}", self.duration_in_minutes, document=self))
        self.user_ramp_up = random.randint(1, 3)

    def __str__(self):
        return f"Document: doc_id: {self.doc_id}, duration_in_minutes: {self.duration_in_minutes}, total_users: {len(self.users)}"

    async def run(self):
        tasks = []
        for each_user in self.users:
            task = asyncio.create_task(each_user.do_work())
            tasks.append(task)
        # print(f"*** doc: {self.doc_id}, user_tasks: {len(tasks)}")
        await asyncio.gather(*tasks)

class User:
    def __init__(self, id, session_duration_in_minutes, document):
        self.id = id
        self.document = document
        self.profile = UserProfile.new(random.choice(UserProfile.types()))
        self.engagement_duration_in_minutes = random.randint(1, session_duration_in_minutes)
        total_engagements = self.engagement_duration_in_minutes * 60 / User.each_engagement_duration_in_seconds() 
        engagement_profile = []
        engagement_profile.extend([HeavyEngagement()] * math.ceil(total_engagements * self.profile.heavy))
        engagement_profile.extend([MediumEngagement()] * math.ceil(total_engagements * self.profile.medium))
        engagement_profile.extend([LowEngagement()] * math.ceil(total_engagements * self.profile.low))
        random.shuffle(engagement_profile)
        self.engagement_profile = engagement_profile

    async def do_work(self):
        edits = 1
        total_engagements_completed = 0
        for eng_profile in self.engagement_profile:
            sleep_for = eng_profile.delta_generation_interval_in_seconds
            work_duration = 0
            while work_duration <= User.each_engagement_duration_in_seconds(): 
                await asyncio.sleep(sleep_for)
                is_write_delta = random.choice([True, False])
                actual_work_done = 0
                # now = str(int(round(time.time() * 1000)))
                now = datetime.now().isoformat()
                print(f"{now},{cfg['simulation_run_id']},{self.id},{self.document.urn},{self.profile.type},{is_write_delta},{len(self.engagement_profile)},{total_engagements_completed},{edits}")
                edits += 1
                work_duration = work_duration + sleep_for + actual_work_done
            total_engagements_completed += 1
    @staticmethod
    def each_engagement_duration_in_seconds():
        return 30

class UserProfile:
    def __init__(self, type, heavy, medium, low):
        self.type = type
        self.heavy = heavy
        self.medium = medium
        self.low = low
    @staticmethod
    def types():
        return ['power', 'regular', 'casual']

    @classmethod
    def new(cls, type):
        if type == 'power':
            return UserProfile(
                type=type, 
                heavy=cfg['user_profile']['power']['heavy_pct'], 
                medium=cfg['user_profile']['power']['medium_pct'], 
                low=cfg['user_profile']['power']['low_pct'] )
        elif type == 'regular':
            return UserProfile(
                type=type, 
                heavy=cfg['user_profile']['regular']['heavy_pct'], 
                medium=cfg['user_profile']['regular']['medium_pct'], 
                low=cfg['user_profile']['regular']['low_pct'] )
        else:
            return UserProfile(
                type=type, 
                heavy=cfg['user_profile']['casual']['heavy_pct'], 
                medium=cfg['user_profile']['casual']['medium_pct'], 
                low=cfg['user_profile']['casual']['low_pct'] )

class Engagement:
    def __init__(self, delta_generation_interval_in_seconds):
        self.delta_generation_interval_in_seconds = delta_generation_interval_in_seconds

class HeavyEngagement(Engagement):
    def __init__(self):
        super().__init__(delta_generation_interval_in_seconds=cfg['engagement']['delta_generation_every_n_seconds_per_interval']['heavy'])

class MediumEngagement(Engagement):
    def __init__(self):
        super().__init__(delta_generation_interval_in_seconds=cfg['engagement']['delta_generation_every_n_seconds_per_interval']['medium'])

class LowEngagement(Engagement):
    def __init__(self):
        super().__init__(delta_generation_interval_in_seconds=cfg['engagement']['delta_generation_every_n_seconds_per_interval']['low'])


async def main():
    start_timestamp = datetime.now()
    start = time.monotonic()
    simulation_duration_in_seconds = cfg['simulation_duration_in_seconds']
    tasks = []
    for session_num in range(1, simulation_duration_in_seconds + 1):
        doc_id = 1
        _range = cfg['doc_sessions_to_generate_range']
        total_docs_per_session = random.randint(_range[0], _range[1]) # this amount of doc editing sessions every second
        sessions = []
        for i in range(total_docs_per_session):
            session = DocSession(f"doc:doc-{session_num}-{doc_id}")
            doc_id += 1
            now = datetime.now()
            # print(f"{now},{session}")
            sessions.append(session)
        for each_session in sessions:
            task = asyncio.create_task(each_session.run())
            tasks.append(task)
        await asyncio.sleep(cfg['generate_doc_sessions_in_every_n_seconds']) 
    await asyncio.gather(*tasks)
    end = time.monotonic()
    # print(f"***** simulation duration: {round((end - start), 2)} *****")
    with open('summary.log', 'w') as f:
        duration = str(timedelta(seconds=round((end - start), 2)))
        f.write(f"simulation_run: {cfg['simulation_run_id']} start_at: {start_timestamp.isoformat()} duration: {duration}\n")
        f.write(f"{json.dumps(cfg, indent=2)}\n")


cfg = json.loads(open('config.json').read())
asyncio.run(main())