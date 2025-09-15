<?php
declare(strict_types=1);

use Phinx\Seed\AbstractSeed;

final class UserApartmentSeeder extends AbstractSeed
{
    public function run(): void
    {
        // Assuming first user and first apartment inserted by previous seeds
        $data = [
            [
                'user_id' => 1,
                'apartment_id' => 1,
                'role' => 'resident',
                'created_at' => date('Y-m-d H:i:s'),
                'modified_at' => date('Y-m-d H:i:s'),
            ],
        ];

        $userApartment = $this->table('user_apartment');
        $userApartment->insert($data)->save();
    }
}




















































                    